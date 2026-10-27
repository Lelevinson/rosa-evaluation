"""Edit genuine isolated Gazebo camera recordings; speed changes are labeled."""
from bisect import bisect_right
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import textwrap

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/macro-m5-20261027'
FPS = 10
SIZE = (1280, 720)
FONT = Path('C:/Windows/Fonts/arial.ttf')


def font(size):
    return ImageFont.truetype(str(FONT), size)


@lru_cache(maxsize=8)
def picture(path):
    with Image.open(path) as image:
        return image.convert('RGB').copy()


def text(draw, xy, value, size=23, color='#dae7f1', width=35):
    x, y = xy
    for line in str(value).splitlines():
        for wrapped in textwrap.wrap(line, width=width) or ['']:
            draw.text((x, y), wrapped, fill=color, font=font(size))
            y += size + 8
    return y


def card(title, subtitle, seconds, encoder):
    canvas = Image.new('RGB', SIZE, '#0d1c2c')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((45, 80, 55, 610), fill='#35b6a4')
    text(draw, (85, 100), title, 43, width=45)
    text(draw, (85, 280), subtitle, 27, width=70)
    draw.text((85, 650), 'ROSA / M5 / 2026-10-27', font=font(20), fill='#9bb0c4')
    value = canvas.tobytes()
    for _ in range(int(seconds * FPS)):
        encoder.stdin.write(value)


def record(backend):
    folder = OUT / ('demo-' + backend)
    result = json.loads((folder / 'result.json').read_text())
    frames = json.loads((folder / 'frames.json').read_text())
    times = [f['seconds'] for f in frames]
    changes = []
    for a, b in zip(frames, frames[1:]):
        delta = ImageChops.difference(picture(str(folder / 'frames' / a['file'])), picture(str(folder / 'frames' / b['file'])))
        changes.append(sum(ImageStat.Stat(delta).mean) / 3)
    threshold = max(.025, max(changes) * .08)
    moving = [i + 1 for i, value in enumerate(changes) if value >= threshold]
    assert moving, 'No visible movement in camera recording; do not fabricate it'
    start = max(times[0], result['model_started_seconds'] - 2)
    end = min(times[-1], result['model_finished_seconds'] + 4)
    motion_start = max(start, times[moving[0]] - 1)
    motion_end = min(end, times[moving[-1]] + 1)
    return {'backend': backend, 'folder': folder, 'result': result, 'frames': frames, 'times': times,
            'segments': [(start, motion_start, 8), (motion_start, motion_end, 1), (motion_end, end, 8)],
            'motion_threshold': threshold, 'model_loop_seconds': result['model_finished_seconds'] - result['model_started_seconds']}


def render(data, source_time, speed):
    backend, result = data['backend'], data['result']
    label = 'Hosted Sol' if backend == 'siwc' else 'Local Qwen3.5 9B'
    index = max(0, bisect_right(data['times'], source_time) - 1)
    frame = data['frames'][index]
    canvas = Image.new('RGB', SIZE, '#0d1c2c')
    canvas.paste(picture(str(data['folder'] / 'frames' / frame['file'])), (25, 85))
    draw = ImageDraw.Draw(canvas)
    draw.text((25, 22), label + ' | actual Gazebo camera recording', font=font(29), fill='#f2f7fa')
    y = text(draw, (855, 95), 'Requested goal', 23, '#58d3c1')
    y = text(draw, (855, y + 4), 'ur5e.offset\nPan +0.18 rad\nFinal wrist +0.16 rad', 23)
    finished = source_time >= result['model_finished_seconds'] + 1
    status = 'INDEPENDENT GOAL VERIFIED' if finished and result['pass'] else 'MODEL / BOUNDED TOOL LOOP'
    y = text(draw, (855, y + 15), status, 23, '#58d3c1' if finished else '#f0c36a')
    if finished:
        y = text(draw, (855, y + 8), f"{result['live_model_requests']} model calls\n{len(result['snapshot']['operations'])} native operations\n{result['inference']['known_output_tokens']} output tokens\n{data['model_loop_seconds']:.2f}s model/tool loop", 21)
    else:
        y = text(draw, (855, y + 8), 'Python: read, conditional move, fresh verification.\nModel: select skill, classify evidence.', 21)
    badge = 'WAITING / 8x PLAYBACK' if speed == 8 else 'CAMERA MOTION / 1x PLAYBACK'
    draw.rectangle((35, 100, 475, 140), fill='#10283a')
    draw.text((45, 107), badge, font=font(20), fill='#ffffff')
    draw.text((35, 650), f'Recorded elapsed: {source_time:.1f}s | camera 5 fps | encoded 10 fps', font=font(19), fill='#ffffff')
    draw.text((25, 692), 'M5 presentation run; not an additional M4 trial. Camera rendering affects timing.', font=font(18), fill='#9bb0c4')
    return canvas


def main():
    encoder_path = shutil.which('ffmpeg')
    assert encoder_path
    video = OUT / 'ROSA_M5_GAZEBO_DEMONSTRATION.mp4'
    assert not video.exists(), 'Do not overwrite presentation evidence'
    log = (OUT / 'video-encoding.log').open('w')
    command = [encoder_path, '-hide_banner', '-loglevel', 'warning', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', '1280x720', '-r', str(FPS), '-i', 'pipe:0', '-an', '-c:v', 'libx264',
               '-preset', 'veryfast', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log,
                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    records = [record(b) for b in ('siwc', 'ollama')]
    try:
        card('Bounded robotic macros in ROSA',
             'Six-joint UR5e in Gazebo.\nReal model decisions; deterministic bounded execution.\nFresh independent final-joint checks.\nNew presentation runs, separate from frozen M4 research.', 5, encoder)
        for data in records:
            label = 'Hosted Sol' if data['backend'] == 'siwc' else 'Local Qwen3.5 9B'
            card(label + ': one recorded take',
                 'Identical explicit request: move to ur5e.offset.\nWaiting is accelerated and labeled; camera motion plays at 1x.\nNo command replay and no repeated takes to obtain success.', 4, encoder)
            for begin, end, speed in data['segments']:
                when = begin
                while when < end:
                    encoder.stdin.write(render(data, when, speed).tobytes())
                    when += speed / FPS
            last = render(data, data['times'][-1], 1)
            last.save(OUT / ('video-final-' + data['backend'] + '.png'))
            for _ in range(3 * FPS):
                encoder.stdin.write(last.tobytes())
        card('What this demonstration establishes',
             'Both recorded runs reached the requested pose: 2 model calls each.\nM4 research remains mixed: Sol 20/20 vs 20/20; Qwen 15/20 vs 14/20.\nThis video is not evidence of general reliability or hardware safety.\nSee the research report, claim ledger and preserved raw evidence.', 7, encoder)
    finally:
        encoder.stdin.close()
        code = encoder.wait(timeout=120)
        log.close()
    assert code == 0
    # ffprobe is distributed beside the existing ffmpeg executable.
    probe = shutil.which('ffprobe')
    metadata = json.loads(subprocess.check_output([probe, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(video)]))
    status = {'video': video.name, 'sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
        'bytes': video.stat().st_size, 'duration_seconds': float(metadata['format']['duration']),
        'dimensions': [metadata['streams'][0]['width'], metadata['streams'][0]['height']],
        'new_demo_model_requests': sum(d['result']['live_model_requests'] for d in records),
        'new_research_trials': 0, 'real_gazebo_camera': True, 'desktop_capture': False,
        'editing': 'Waiting segments8x, visible-motion segment1x, labeled. Timestamp-based frame hold; no generated/interpolated motion.',
        'motion_window_selection': 'Consecutive camera-image differences, not a causal controller-dispatch timing assertion.',
        'backends': {d['backend']: {'independent_goal_verified': d['result']['pass'],
                     'model_loop_seconds': d['model_loop_seconds'], 'segments': d['segments']} for d in records}}
    (OUT / 'video-provenance.json').write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps(status, indent=2))


if __name__ == '__main__': main()
