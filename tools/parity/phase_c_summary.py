"""Parity helpers for the chain (read-only; zero model calls).

  phase_c_summary.py summary   <run_dir>   frozen G1 engine summary (adjudication.summarize, empty human-review
                                           bundle: ambiguous stay PENDING) -> <run_dir>/PHASE_C_SUMMARY.json
  phase_c_summary.py evaluable <run_dir>   ACCEPTANCE_CRITERIA §4 'incomplete' check: per arm, tool tasks that are
                                           evaluable (not infrastructure-censored under G1 V1) -> EVALUABLE.json
"""
import json
import os
from pathlib import Path
import sys

WS = Path(os.environ.get('PARITY_WORKSPACE', '/mnt/c/Proj/robotics/introtorobotics'))
G1 = WS / 'rosa-evaluation/artifacts/macro-generalization-20261113/revision-1'
ADJ = G1 / 'stage-3/clarification-scoring-v2-20261119'
sys.path[:0] = [str(WS / 'rosa-research/src'), str(G1), str(G1 / 'stage-2'), str(ADJ), str(G1 / 'stage-3')]


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def main():
    mode, run = sys.argv[1], Path(sys.argv[2])
    rows = [read(p) for p in sorted((run / 'trials').glob('*/result.json'))]
    if mode == 'summary':
        from adjudication import summarize, VERSION
        rubric = read(ADJ / 'LEV_ACTUAL_REVIEW_BOUND.json')['rubric_sha256']
        bundle = {'version': VERSION, 'rubric_sha256': rubric, 'records': []}
        plan = [i['id'] for i in read(run / 'plan.json')]
        out = summarize(rows, plan, bundle, rubric)
        out.update(label='adapted-integration rerun (laptop)', model_requests_by_this_script=0)
        (run / 'PHASE_C_SUMMARY.json').write_text(json.dumps(out, indent=1, default=str) + '\n', encoding='utf-8')
        print(json.dumps(out['counts']))
    elif mode == 'evaluable':
        from censoring import censor_class
        arms = {}
        for r in rows:
            if r['case']['kind'] == 'ambiguous':
                continue
            a = arms.setdefault(r['mode'], {'tool_tasks': 0, 'evaluable': 0})
            a['tool_tasks'] += 1
            a['evaluable'] += censor_class(r) is None
        planned = {}
        for i in read(run / 'plan.json'):
            if i['case']['kind'] != 'ambiguous':
                planned[i['mode']] = planned.get(i['mode'], 0) + 1
        incomplete = any(arms.get(m, {}).get('evaluable', 0) < n - 1 for m, n in planned.items())  # < 8 of 9
        out = {'arms': arms, 'planned_tool_tasks': planned, 'incomplete': incomplete}
        (run / 'EVALUABLE.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
        print(json.dumps(out))


if __name__ == '__main__':
    main()
