"""Fixed run order for Gazebo D dev (D1) and held-out (D2). Stdlib only, deterministic, zero model calls.

Rules (D0_PROTOCOL §6):
  - held-out case order: random.Random(SEED).shuffle of the 20 held-out ids; dev: listed order;
  - one Gazebo instance; models interleaved BY CASE: every model runs both arms of a case before the next
    case starts, so a late stop leaves whole cases for every model (balanced partial data);
  - model order rotates by one position per case (no model is always first or last);
  - arm order alternates within each template group: the group's first case (in run order) gets
    primitives->macro if the group number is odd, else macro->primitives; its second case gets the reverse.
    Every model uses the same arm order for a given case;
  - models not admitted by Phase B are dropped from the list at launch; the rest keep their order.
Writes artifacts/gazebo-d-20261121/schedule/{dev,heldout}.json.
Usage: python -I -B tools/gazebo_d/schedule.py
"""
import hashlib
import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CASES = REPO / 'artifacts/gazebo-d-20261121/cases'
OUT = REPO / 'artifacts/gazebo-d-20261121/schedule'
SEED = 20261121
MODELS = ['sol', 'qwen', 'ministral', 'granite', 'llama']   # granite/llama only if admitted in Phase B


def plan(cases, shuffle):
    order = list(cases)
    if shuffle:
        random.Random(SEED).shuffle(order)
    seen = {}
    rows = []
    for position, c in enumerate(order):
        group = c['template_group']
        number = int(group.rsplit('.', 1)[1].lstrip('Gd') or 0)
        first_is_primitives = (number % 2 == 1)
        if group in seen:
            first_is_primitives = not seen[group]
        seen.setdefault(group, first_is_primitives)
        arms = ('primitives', 'macro') if first_is_primitives else ('macro', 'primitives')
        k = position % len(MODELS)
        models = MODELS[k:] + MODELS[:k]
        for model in models:
            for arm in arms:
                rows.append({'seq': len(rows) + 1, 'case_position': position + 1, 'case': c['id'],
                             'template_group': group, 'model': model, 'arm': arm})
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for split, shuffle in (('dev', False), ('heldout', True)):
        cases = json.loads((CASES / f'{split}.json').read_text(encoding='utf-8'))
        rows = plan(cases, shuffle)
        data = (json.dumps({'seed': SEED if shuffle else None, 'models_full_set': MODELS,
                            'trials_full_set': len(rows), 'rows': rows}, indent=1) + '\n').encode('utf-8')
        (OUT / f'{split}.json').write_bytes(data)
        print(split, len(rows), hashlib.sha256(data).hexdigest())
        if shuffle:
            print(' case order:', list(dict.fromkeys(r['case'] for r in rows)))


if __name__ == '__main__':
    main()
