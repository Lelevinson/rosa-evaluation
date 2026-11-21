"""Leakage check for the Gazebo D cases, reusing the F1 checker unchanged (metric, normalization, thresholds).

The F1 checker (tools/f1_wording/leakage_check.py on member/martin-f1) is read with `git show`; its blob
hash is recorded. References:
  - the 10 frozen M4 requests (experiments/macro_m4/design.py, read as text from the frozen M4 freeze.json);
  - the F1 references(): 5 M4 + 7 G1 length-stop requests, 38 G1 held-out, 18 G1 dev;
  - the 30 F1 held-out requests;
  - for held-out cases also the 6 D dev cases (dev must not paraphrase held-out).
Pose names are compared raw (not normalized away), which is the stricter choice.

Writes artifacts/gazebo-d-20261121/cases/LEAKAGE_CHECK.{json,md}. Zero model calls.
Usage: python -I -B tools/gazebo_d/leakage_check.py
"""
import json
import subprocess
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CASES = REPO / 'artifacts/gazebo-d-20261121/cases'
M4_FREEZE = REPO / 'artifacts/macro-m4-20261027/freeze.json'
F1_BRANCH = 'member/martin-f1'
F1_CHECKER = 'tools/f1_wording/leakage_check.py'
F1_HELDOUT = 'artifacts/f1-catalogue-wording-20261121/cases/heldout.json'


def git(*args):
    return subprocess.run(['git', '-C', str(REPO), *args], check=True, capture_output=True).stdout


def load_f1_checker():
    src = git('show', f'{F1_BRANCH}:{F1_CHECKER}').decode('utf-8')
    mod = types.ModuleType('f1_leakage_check')
    mod.__file__ = str(REPO / F1_CHECKER)
    exec(compile(src, F1_CHECKER, 'exec'), mod.__dict__)
    return mod, git('rev-parse', f'{F1_BRANCH}:{F1_CHECKER}').decode().strip()


def verdict(m, seq, jac):
    return ('NEAR-PARAPHRASE' if seq >= m.SEQ_REWRITE or jac >= m.JAC_REWRITE else
            'REVIEW' if seq >= m.SEQ_REVIEW or jac >= m.JAC_REVIEW else 'OK')


def check(m, cases, refs):
    rows = []
    for c in cases:
        scored = [(label, *m.compare(c['request'], text)) for label, text in refs if text != c['request']]
        by_seq = max(scored, key=lambda s: (s[1], s[2]))
        by_jac = max(scored, key=lambda s: (s[2], s[1]))
        rows.append({'id': c['id'], 'family': c['family'], 'verdict': verdict(m, by_seq[1], by_jac[2]),
                     'nearest_by_sequence': {'reference': by_seq[0], 'seq': by_seq[1], 'jac': by_seq[2]},
                     'nearest_by_content_words': {'reference': by_jac[0], 'seq': by_jac[1], 'jac': by_jac[2]}})
    return rows


def main():
    m, blob = load_f1_checker()
    m4 = [('M4 ' + c['id'], c['request']) for c in json.loads(M4_FREEZE.read_text(encoding='utf-8'))['cases']]
    f1 = [('F1 ' + c['case_id'], c['request'])
          for c in json.loads(git('show', f'{F1_BRANCH}:{F1_HELDOUT}').decode('utf-8'))]
    dev = json.loads((CASES / 'dev.json').read_text(encoding='utf-8'))
    held = json.loads((CASES / 'heldout.json').read_text(encoding='utf-8'))
    base = m4 + m.references() + f1
    dev_refs = [('D ' + c['id'], c['request']) for c in dev]
    held_refs = [('D ' + c['id'], c['request']) for c in held]
    rows = {'dev': check(m, dev, base + held_refs), 'heldout': check(m, held, base + dev_refs + held_refs)}
    summary = {n: {v: sum(r['verdict'] == v for r in rs) for v in ('OK', 'REVIEW', 'NEAR-PARAPHRASE')}
               for n, rs in rows.items()}
    result = {'f1_checker': {'branch': F1_BRANCH, 'path': F1_CHECKER, 'git_blob': blob},
              'references': {'m4': len(m4), 'f1_reference_set': len(m.references()), 'f1_heldout': len(f1),
                             'd_dev': len(dev), 'd_heldout': len(held)},
              'thresholds': {'rewrite': {'seq': m.SEQ_REWRITE, 'jac': m.JAC_REWRITE},
                             'review': {'seq': m.SEQ_REVIEW, 'jac': m.JAC_REVIEW}},
              'summary': summary, 'rows': rows, 'model_requests': 0}
    (CASES / 'LEAKAGE_CHECK.json').write_bytes((json.dumps(result, indent=1) + '\n').encode('utf-8'))
    md = ['# Leakage check: Gazebo D dev and held-out cases', '',
          f'F1 checker reused unchanged (`{F1_BRANCH}:{F1_CHECKER}`, blob `{blob}`). References: '
          f'{len(m4)} M4 requests, {len(m.references())} F1 reference requests (M4/G1 length-stops, G1 held-out, '
          f'G1 dev), {len(f1)} F1 held-out, and every other D case (dev vs held-out and within held-out). '
          f'Rewrite if seq >= {m.SEQ_REWRITE} or jac >= {m.JAC_REWRITE}; REVIEW if seq >= {m.SEQ_REVIEW} or '
          f'jac >= {m.JAC_REVIEW}. Pose names are not normalized (stricter).', '',
          f'**Summary:** {summary}', '',
          '| Case | Verdict | Nearest (word sequence) | seq | Nearest (content words) | jac |', '|---|---|---|---:|---|---:|']
    for n in ('dev', 'heldout'):
        for r in rows[n]:
            s, j = r['nearest_by_sequence'], r['nearest_by_content_words']
            md.append(f"| {r['id']} | {r['verdict']} | {s['reference']} | {s['seq']:.2f} | {j['reference']} | "
                      f"{j['jac']:.2f} |")
    (CASES / 'LEAKAGE_CHECK.md').write_bytes(('\n'.join(md) + '\n').encode('utf-8'))
    print('summary', summary)
    for n in rows:
        for r in rows[n]:
            if r['verdict'] != 'OK':
                print(r['id'], r['verdict'], r['nearest_by_sequence'], r['nearest_by_content_words'])


if __name__ == '__main__':
    main()
