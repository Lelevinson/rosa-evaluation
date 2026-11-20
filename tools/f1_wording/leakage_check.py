"""Leakage check: each F1 held-out request vs the 12 length-stop requests, all G1 held-out and G1 dev.

Stdlib only, deterministic, read-only on frozen evidence. Writes cases/LEAKAGE_CHECK.{json,md}.

Normalization (applied to both sides): lower-case; the two domain nouns -> <d>; the frozen
coordinate strings -> <c>; any run of readiness check names -> <k>; punctuation removed.
These parts are forced to be identical by the frozen worlds, so they must not count as overlap.

Metrics against every reference:
  seq  = difflib.SequenceMatcher ratio over normalized word sequences;
  jac  = Jaccard over content-word sets (stop words removed).
Rule fixed before the first run: a case is a NEAR-PARAPHRASE, to be rewritten, if
seq >= 0.60 or jac >= 0.50 against any reference. 0.45 <= seq < 0.60 or 0.35 <= jac < 0.50 is
flagged REVIEW (kept, but listed). This is a lexical check; it cannot detect a shared task concept
(e.g. "move only if current position evidence exists" is the movement-with-prerequisite task type
itself, which the brief requires).

Usage:  python -I -B tools/f1_wording/leakage_check.py
"""
import difflib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CASES = REPO / 'artifacts/f1-catalogue-wording-20261121/cases'
G1 = REPO / 'artifacts/macro-generalization-20261113/revision-1'
M4 = REPO / 'artifacts/macro-m4-20261027/ollama'
M4_LENGTH_STOPS = ['09-missing_prerequisite-r1-primitives', '10-missing_prerequisite-r1-macro',
                   '31-move_constrained-r2-primitives', '37-partial_command-r2-macro',
                   '39-missing_prerequisite-r2-primitives']
G1_LENGTH_STOPS = ['030-primitives', '031-macro', '031-primitives', '032-macro', '032-primitives',
                   '033-primitives', '051-macro']
SEQ_REWRITE, JAC_REWRITE, SEQ_REVIEW, JAC_REVIEW = .60, .50, .45, .35
STOP = set('a an the of to for and or on in at is are be it its this that these those with by as if '
           'any no not only then from me my i you your please there their what which whether all every '
           'one do does so but should may can must has have before after up'.split())
CHECK_NAMES = ('guard_closed joint_sample_fresh brake_released temperature_safe workspace_clear tool_mount_locked '
               'pose_fix_valid map_lease_valid reserve_sufficient path_clear odometry_consistent '
               'traction_sufficient').split()


def normalize(text):
    t = text.lower()
    t = t.replace('articulated test fixture', ' <d> ').replace('delivery platform', ' <d> ')
    t = t.replace('yaw=-0.18 radian, pitch=0.11 radian', ' <c> ')
    t = t.replace('x_m=1.2 metre, y_m=-0.6 metre, heading_fraction=0.25 fraction of full turn', ' <c> ')
    t = re.sub(r'(?:\b(?:' + '|'.join(CHECK_NAMES) + r')\b[\s,]*)+', ' <k> ', t)
    t = re.sub(r"[^a-z0-9<>_' -]", ' ', t)
    return t.split()


def content(words):
    return {w for w in words if w not in STOP and not w.startswith('<')}


def compare(a, b):
    wa, wb = normalize(a), normalize(b)
    seq = difflib.SequenceMatcher(None, wa, wb, autojunk=False).ratio()
    ca, cb = content(wa), content(wb)
    jac = len(ca & cb) / len(ca | cb) if ca | cb else 0.0
    return round(seq, 3), round(jac, 3)


def references():
    refs = []
    for t in M4_LENGTH_STOPS:
        r = json.loads((M4 / t / 'result.json').read_text(encoding='utf-8'))
        refs.append(('length-stop M4 ' + t, r['request']))
    g1 = {c['case_id']: c for c in json.loads((G1 / 'cases.json').read_text(encoding='utf-8-sig'))}
    for t in G1_LENGTH_STOPS:
        refs.append(('length-stop G1 ' + t, g1['G1r1-heldout-' + t.split('-')[0]]['request']))
    refs += [('G1 ' + cid[5:], c['request']) for cid, c in g1.items()]
    return refs


def main():
    refs = references()
    heldout = json.loads((CASES / 'heldout.json').read_text(encoding='utf-8'))
    rows = []
    for c in heldout:
        scored = [(label, *compare(c['request'], text)) for label, text in refs]
        by_seq = max(scored, key=lambda s: (s[1], s[2]))
        by_jac = max(scored, key=lambda s: (s[2], s[1]))
        stops = [s for s in scored if s[0].startswith('length-stop')]
        near_stop = max(stops, key=lambda s: (s[1], s[2]))
        verdict = ('NEAR-PARAPHRASE' if by_seq[1] >= SEQ_REWRITE or by_jac[2] >= JAC_REWRITE else
                   'REVIEW' if by_seq[1] >= SEQ_REVIEW or by_jac[2] >= JAC_REVIEW else 'OK')
        rows.append({'case_id': c['case_id'], 'f1_type': c['f1_type'], 'verdict': verdict,
                     'nearest_by_sequence': {'reference': by_seq[0], 'seq': by_seq[1], 'jac': by_seq[2]},
                     'nearest_by_content_words': {'reference': by_jac[0], 'seq': by_jac[1], 'jac': by_jac[2]},
                     'nearest_length_stop': {'reference': near_stop[0], 'seq': near_stop[1], 'jac': near_stop[2]}})
    summary = {v: sum(r['verdict'] == v for r in rows) for v in ('OK', 'REVIEW', 'NEAR-PARAPHRASE')}
    result = {'thresholds': {'rewrite': {'seq': SEQ_REWRITE, 'jac': JAC_REWRITE},
                             'review': {'seq': SEQ_REVIEW, 'jac': JAC_REVIEW}},
              'references': len(refs), 'reference_labels': [label for label, _ in refs],
              'summary': summary, 'rows': rows}
    (CASES / 'LEAKAGE_CHECK.json').write_bytes((json.dumps(result, indent=1) + '\n').encode('utf-8'))
    md = ['# Leakage check: F1 held-out vs length-stop, G1 held-out and G1 dev requests', '',
          'Generated by `tools/f1_wording/leakage_check.py` (deterministic, stdlib only). '
          f'References: {len(refs)} (5 M4 + 7 G1 length-stop trials, 38 G1 held-out, 16 G1 dev). '
          'Domain nouns, coordinate strings and check names are normalized away first. '
          f'Rewrite if seq >= {SEQ_REWRITE} or jac >= {JAC_REWRITE}; '
          f'REVIEW if seq >= {SEQ_REVIEW} or jac >= {JAC_REVIEW}.', '',
          f'**Summary:** {summary}', '',
          '| Case | Type | Verdict | Nearest (word sequence) | seq | Nearest (content words) | jac | Nearest length-stop | seq / jac |',
          '|---|---|---|---|---:|---|---:|---|---|']
    for r in rows:
        s, j, l = r['nearest_by_sequence'], r['nearest_by_content_words'], r['nearest_length_stop']
        md.append(f"| {r['case_id']} | {r['f1_type']} | {r['verdict']} | {s['reference']} | {s['seq']:.2f} | "
                  f"{j['reference']} | {j['jac']:.2f} | {l['reference']} | {l['seq']:.2f} / {l['jac']:.2f} |")
    (CASES / 'LEAKAGE_CHECK.md').write_bytes(('\n'.join(md) + '\n').encode('utf-8'))
    print('summary', summary)
    for r in rows:
        if r['verdict'] != 'OK':
            print(r['case_id'], r['verdict'], r['nearest_by_sequence'], r['nearest_by_content_words'])


if __name__ == '__main__':
    main()
