"""Pre-registered Stage 1a dev diagnostic (PROTOCOL §5 step 2, D9). Read-only; no model access.

For every Qwen dev trial, scan the model's visible output text (content of every model output, not tool
arguments) case-insensitively for readiness / inspect-first deliberation:
  'readiness', 'inspect first', 'inspect ... before', 'check ... before', 'before moving'.
Flagged trials must then be read manually and the reading recorded in DEV_REVISION_LOG.md.
Usage: dev_diagnostic.py --run <run name> --out <json>
"""
import argparse
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[1] / 'artifacts/f1-catalogue-wording-20261121'
PATTERNS = {
    'readiness': re.compile(r'readiness', re.I),
    'inspect first': re.compile(r'inspect\s+first', re.I),
    'inspect ... before': re.compile(r'inspect\w*\b.{0,80}?\bbefore\b', re.I | re.S),
    'check ... before': re.compile(r'check\w*\b.{0,80}?\bbefore\b', re.I | re.S),
    'before moving': re.compile(r'before\s+moving', re.I),
}


def visible_text(row):
    parts = []
    for out in row.get('model_outputs') or []:
        content = out.get('content')
        if isinstance(content, list):
            content = ' '.join(c.get('text', '') for c in content if isinstance(c, dict))
        if content:
            parts.append(content)
    return '\n---\n'.join(parts)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', required=True)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    rows = []
    for f in sorted((STUDY / 'runs' / a.run / 'trials').glob('*/result.json')):
        r = json.loads(f.read_text(encoding='utf-8'))
        text = visible_text(r)
        hits = {k: [m.group(0)[:120] for m in rx.finditer(text)][:5] for k, rx in PATTERNS.items()}
        hits = {k: v for k, v in hits.items() if v}
        rows.append({'id': r['id'], 'arm': r['f1_arm'], 'f1_type': r['f1_type'], 'flagged': bool(hits), 'hits': hits,
                     'primary_pass_raw': r['primary_pass'], 'length_stop': r['score'].get('length_stop'),
                     'selected': r['snapshot'].get('selected_skill'), 'calls': r['inference']['calls'],
                     'visible_text_chars': len(text), 'visible_text_excerpt': text[:1500]})
    summary = {a2: {'trials': sum(r['arm'] == a2 for r in rows), 'flagged': sum(r['flagged'] and r['arm'] == a2 for r in rows)}
               for a2 in ('base', 'new')}
    a.out.write_text(json.dumps({'patterns': list(PATTERNS), 'summary': summary, 'rows': rows}, indent=1) + '\n',
                     encoding='utf-8')
    print(json.dumps(summary))
    for r in rows:
        if r['flagged']:
            print(r['id'], r['f1_type'], 'pass' if r['primary_pass_raw'] else 'FAIL', list(r['hits']))


if __name__ == '__main__':
    main()
