"""A0 load-only check (owner-approved): load each model on the parity server with num_ctx 8192 and an EMPTY
prompt (Ollama 'load a model' API: no prompt -> no generation), record /api/ps, GPU offload from the server
log, VRAM and load time, then unload (keep_alive 0). Zero generated tokens.
Usage: python -I load_check.py <out.json>"""
import json, subprocess, sys, time, urllib.request
from pathlib import Path

BASE = 'http://172.31.0.1:11440'
STATE = Path(r'C:\Proj\robotics\introtorobotics\.local\parity-ollama-state')
G1 = {'qwen3.5:9b': ('56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90', 5862210928, '33/33'),
      'ministral-3:8b-instruct-2512-q4_K_M': ('1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71', 6356048280, '35/35'),
      'granite3.3:8b': ('fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7', 6524512501, '41/41'),
      'llama3.1:8b-instruct-q4_K_M': ('46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e', 5951214059, '33/33')}


def call(path, body=None, timeout=600):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def gpu():
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True).stdout.strip().split(',')
    return {'used_mib': int(out[0]), 'total_mib': int(out[1])}


def log_lines(path, start):
    text = path.read_text(encoding='utf-8', errors='replace')[start:]
    keep = [l for l in text.splitlines() if any(k in l for k in ('offloaded', 'flash_attn', 'KV buffer', 'kv_cache: size',
            'starting llama-server', 'gpu memory', 'n_ctx  ', 'model weights', 'llama_context: n_ctx'))]
    return keep


def main():
    out = Path(sys.argv[1])
    proc = json.loads((STATE / 'process.json').read_text(encoding='utf-8-sig'))
    log = STATE / proc['stderr']
    version = call('/api/version')['version']
    tags = {m['name']: m for m in call('/api/tags')['models']}
    results = {'server_version': version, 'endpoint': BASE, 'generated_tokens': 0, 'models': {}}
    for name, (digest, lab_size, lab_layers) in G1.items():
        r = {'tag_present': name in tags, 'digest': tags.get(name, {}).get('digest'),
             'digest_match_G1': tags.get(name, {}).get('digest') == digest, 'download_size': tags.get(name, {}).get('size')}
        if not r['digest_match_G1']:
            results['models'][name] = r
            continue
        assert not call('/api/ps')['models'], 'another model already loaded'
        r['gpu_before'] = gpu()
        start = len(log.read_text(encoding='utf-8', errors='replace'))
        t0 = time.monotonic()
        load = call('/api/generate', {'model': name, 'options': {'num_ctx': 8192}, 'keep_alive': '5m'})
        r['load_seconds'] = round(time.monotonic() - t0, 2)
        r['load_response'] = {k: load.get(k) for k in ('response', 'done', 'done_reason', 'eval_count')}
        time.sleep(1)
        ps = call('/api/ps')['models']
        r['api_ps'] = [{k: m.get(k) for k in ('name', 'digest', 'size', 'size_vram', 'context_length')} for m in ps]
        r['gpu_loaded'] = gpu()
        r['server_log'] = log_lines(log, start)
        layers = [l for l in r['server_log'] if 'offloaded' in l]
        r['layers_on_gpu'] = layers[-1].split('offloaded ')[-1].split(' layers')[0] if layers else 'NOT_IN_LOG'
        r['fully_gpu_resident'] = bool(ps) and ps[0].get('size_vram') == ps[0].get('size')
        r['lab_G1'] = {'size_vram': lab_size, 'layers': lab_layers, 'fully_gpu_resident': True}
        call('/api/generate', {'model': name, 'keep_alive': 0})
        for _ in range(30):
            if not call('/api/ps')['models']:
                break
            time.sleep(1)
        r['unloaded'] = not call('/api/ps')['models']
        r['gpu_after_unload'] = gpu()
        results['models'][name] = r
        print(name, r['digest_match_G1'], r['layers_on_gpu'], r['load_seconds'], r['fully_gpu_resident'], flush=True)
    out.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
