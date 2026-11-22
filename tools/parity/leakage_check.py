"""Leakage check for the parity scratch/acceptance tasks, reusing the F1 checker unchanged.

The F1 checker (tools/f1_wording/leakage_check.py) lives on branch member/martin-f1. It is read
with `git show`, its blob hash is recorded, and its own compare()/references()/thresholds are used
(metric, normalization and REWRITE/REVIEW thresholds identical to F1).

References (all requests):
  - F1 references(): 5 M4 + 7 G1 length-stop requests, 38 G1 held-out, 18 G1 dev;
  - the 30 F1 held-out requests (member/martin-f1);
  - for acceptance tasks also the 12 parity scratch tasks (scratch = development for acceptance).

Writes artifacts/parity-integration-20261121/tasks/LEAKAGE_CHECK.{json,md}. Zero model calls.
Usage: python -I -B tools/parity/leakage_check.py
"""
import json
import subprocess
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / 'artifacts/parity-integration-20261121/tasks'
F1_BRANCH = 'member/martin-f1'
F1_CHECKER = 'tools/f1_wording/leakage_check.py'
F1_HELDOUT = 'artifacts/f1-catalogue-wording-20261121/cases/heldout.json'


def git(*args):
    return subprocess.run(['git', '-C', str(REPO), *args], check=True, capture_output=True).stdout


def load_f1_checker():
    src = git('show', f'{F1_BRANCH}:{F1_CHECKER}').decode('utf-8')
    blob = git('rev-parse', f'{F1_BRANCH}:{F1_CHECKER}').decode().strip()
    mod = types.ModuleType('f1_leakage_check')
    mod.__file__ = str(REPO / F1_CHECKER)   # so its REPO-relative G1/M4 paths resolve in this checkout
    exec(compile(src, F1_CHECKER, 'exec'), mod.__dict__)
    return mod, blob


def verdict(m, seq, jac):
    return ('NEAR-PARAPHRASE' if seq >= m.SEQ_REWRITE or jac >= m.JAC_REWRITE else
            'REVIEW' if seq >= m.SEQ_REVIEW or jac >= m.JAC_REVIEW else 'OK')


def check(m, cases, refs):
    rows = []
    for c in cases:
        scored = [(label, *m.compare(c['request'], text)) for label, text in refs]
        by_seq = max(scored, key=lambda s: (s[1], s[2]))
        by_jac = max(scored, key=lambda s: (s[2], s[1]))
        v = verdict(m, by_seq[1], by_jac[2])
        rows.append({'case_id': c['case_id'], 'parity_type': c['parity_type'], 'verdict': v,
                     'nearest_by_sequence': {'reference': by_seq[0], 'seq': by_seq[1], 'jac': by_seq[2]},
                     'nearest_by_content_words': {'reference': by_jac[0], 'seq': by_jac[1], 'jac': by_jac[2]}})
    return rows


def main():
    m, blob = load_f1_checker()
    f1_blob = git('rev-parse', f'{F1_BRANCH}:{F1_HELDOUT}').decode().strip()
    f1 = json.loads(git('show', f'{F1_BRANCH}:{F1_HELDOUT}').decode('utf-8'))
    base_refs = m.references() + [('F1 ' + c['case_id'], c['request']) for c in f1]
    scratch = json.loads((TASKS / 'scratch.json').read_text(encoding='utf-8'))
    accept = json.loads((TASKS / 'acceptance.json').read_text(encoding='utf-8'))
    acc_refs = base_refs + [('parity ' + c['case_id'], c['request']) for c in scratch]
    # also within-set: no task may paraphrase another task of the same set
    rows = {'scratch': check(m, scratch, base_refs), 'acceptance': check(m, accept, acc_refs)}
    within = {}
    for name, cases in (('scratch', scratch), ('acceptance', accept)):
        worst = []
        for c in cases:
            others = [('parity ' + o['case_id'], o['request']) for o in cases if o['case_id'] != c['case_id']]
            s = max(((lbl, *m.compare(c['request'], t)) for lbl, t in others), key=lambda s: (s[1], s[2]))
            worst.append({'case_id': c['case_id'], 'nearest': s[0], 'seq': s[1], 'jac': s[2],
                          'verdict': verdict(m, s[1], s[2])})
        within[name] = worst
    summary = {n: {v: sum(r['verdict'] == v for r in rs) for v in ('OK', 'REVIEW', 'NEAR-PARAPHRASE')}
               for n, rs in rows.items()}
    within_summary = {n: {v: sum(r['verdict'] == v for r in rs) for v in ('OK', 'REVIEW', 'NEAR-PARAPHRASE')}
                      for n, rs in within.items()}
    result = {'f1_checker': {'branch': F1_BRANCH, 'path': F1_CHECKER, 'git_blob': blob},
              'f1_heldout_blob': f1_blob,
              'thresholds': {'rewrite': {'seq': m.SEQ_REWRITE, 'jac': m.JAC_REWRITE},
                             'review': {'seq': m.SEQ_REVIEW, 'jac': m.JAC_REVIEW}},
              'reference_counts': {'scratch': len(base_refs), 'acceptance': len(acc_refs)},
              'summary': summary, 'within_set_summary': within_summary, 'rows': rows, 'within_set': within,
              'model_requests': 0}
    (TASKS / 'LEAKAGE_CHECK.json').write_bytes((json.dumps(result, indent=1) + '\n').encode('utf-8'))
    md = ['# Leakage check: parity scratch and acceptance tasks', '',
          f'F1 checker reused unchanged: `{F1_BRANCH}:{F1_CHECKER}` (git blob `{blob}`). '
          f'References: {len(base_refs)} for scratch (F1 set: M4/G1 length-stops, G1 held-out, G1 dev; plus 30 '
          f'F1 held-out), {len(acc_refs)} for acceptance (adds the 12 scratch tasks). '
          f'Rewrite if seq >= {m.SEQ_REWRITE} or jac >= {m.JAC_REWRITE}; '
          f'REVIEW if seq >= {m.SEQ_REVIEW} or jac >= {m.JAC_REVIEW}.', '',
          f'**Summary:** {summary}. **Within-set:** {within_summary}.', '',
          '| Task | Type | Verdict | Nearest (word sequence) | seq | Nearest (content words) | jac |',
          '|---|---|---|---|---:|---|---:|']
    for n in ('scratch', 'acceptance'):
        for r in rows[n]:
            s, j = r['nearest_by_sequence'], r['nearest_by_content_words']
            md.append(f"| {r['case_id']} | {r['parity_type']} | {r['verdict']} | {s['reference']} | {s['seq']:.2f} | "
                      f"{j['reference']} | {j['jac']:.2f} |")
    md += ['', 'Within-set nearest neighbour (max seq / jac):', '']
    for n in ('scratch', 'acceptance'):
        for r in within[n]:
            md.append(f"- {r['case_id']}: {r['nearest']} {r['seq']:.2f} / {r['jac']:.2f} ({r['verdict']})")
    (TASKS / 'LEAKAGE_CHECK.md').write_bytes(('\n'.join(md) + '\n').encode('utf-8'))
    print('summary', summary, 'within', within_summary)
    for n in rows:
        for r in rows[n]:
            if r['verdict'] != 'OK':
                print(r['case_id'], r['verdict'], r['nearest_by_sequence'], r['nearest_by_content_words'])
        for r in within[n]:
            if r['verdict'] != 'OK':
                print('within', r)


if __name__ == '__main__':
    main()
