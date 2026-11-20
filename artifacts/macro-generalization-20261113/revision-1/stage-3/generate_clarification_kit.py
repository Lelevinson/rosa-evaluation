"""Create later held-out packets with labels and ratings withheld; no scoring."""
import argparse
import csv
from pathlib import Path
import secrets
from common import ROOT, read, write

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result-roots', type=Path, nargs='+', required=True)
    parser.add_argument('--packet-name', required=True)
    args = parser.parse_args()
    assert args.packet_name.replace('-', '').replace('_', '').isalnum()
    output = ROOT/'clarification-review/generated'/args.packet_name
    output.mkdir(parents=True, exist_ok=False)
    packet = output/'packet'
    packet.mkdir()
    rows = [read(path) for folder in args.result_roots for path in (folder/'trials').glob('*/result.json')]
    rows = [row for row in rows if row['case']['kind'] == 'ambiguous']
    assert rows and len({row['id'] for row in rows}) == len(rows)
    assert all(row['id'].startswith('G1') for row in rows), 'Keep M4 and G1 packets separate'
    secrets.SystemRandom().shuffle(rows)
    key = {}
    with (packet/'ratings-empty.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['case_id', 'reviewer_name', 'appropriate_clarification', 'no_unauthorized_action', 'reason'])
        for index, row in enumerate(rows, 1):
            case = f'C{index:02d}'
            (packet/(case+'.md')).write_text(f'# {case}\n\nUser request:\n\n{row["case"]["request"]}\n\n'
                f'Assistant response:\n\n{row["answer"]}\n\nRecorded tool executions: '
                f'{len(row.get("tool_inputs", []))}. Native attempts: {len(row["actor_records"])}.\n', encoding='utf-8')
            writer.writerow([case, '', '', '', ''])
            key[case] = dict(trial_id=row['id'], model=row.get('model'), condition=row['mode'])
    rubric = (ROOT/'clarification-review/packet/RUBRIC.md').read_text(encoding='utf-8')
    rubric = rubric.replace('This packet has four G1 Stage 2 cases only. It does not contain the eight M4 ambiguity transcripts.',
        f'This packet has {len(rows)} G1 clarification transcripts from the supplied result roots. M4 transcripts remain separate.')
    (packet/'RUBRIC.md').write_text(rubric, encoding='utf-8')
    write(str((output/'private-key.json').relative_to(ROOT)), key)
    write(str((output/'packet-metadata.json').relative_to(ROOT)), dict(transcripts=len(rows), ratings_generated=0,
        source='Provided result roots; keep G1 and M4 separately', send_to_reviewer='packet/ only',
        model_requests=0, rule='Review after authoring is complete; uninvolved reviewer required'))
    print({'packet_transcripts': len(rows), 'ratings_generated': 0})

if __name__ == '__main__':
    main()
