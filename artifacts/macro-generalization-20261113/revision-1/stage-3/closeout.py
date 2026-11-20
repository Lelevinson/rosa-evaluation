"""Report actual gates and a non-launchable preflight; never create a freeze."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import difflib
import json
import shutil
from common import ROOT, REV, WORKSPACE, read, write, digest, check_protected, dev_rows

DECISION5 = 'Run Sol held-out in one uninterrupted authorized session. Resumption may process only unstarted cells under existing authorization and cumulative budgets. The standing recovery instruction does NOT authorize a new held-out launch, changed retry criteria, fresh OAuth consent, altered frozen inputs, reset budgets or a new stage. Copy this paragraph into the Stage 3 pre-run note.'

def proposed_diff():
    path = WORKSPACE/'rosa-research/src/rosa_auth/oauth.py'
    before = path.read_text()
    after = before.replace('def open_request(request, timeout=30):',
                           'def open_request(request, timeout=30, *, on_http_failure=None):', 1)
    after = after.replace('    except HTTPError as error:\n        try:',
                          '    except HTTPError as error:\n        detail = None\n        try:', 1)
    replacement = '''        safe_error = SafeError(error_code(code, 'http_error'), error.code)
        if on_http_failure is not None:
            provider_type = detail.get('type') if isinstance(detail, dict) else None
            allowed_types = {'server_error', 'rate_limit_error', 'invalid_request_error', 'insufficient_quota'}
            metadata = {'failure_surface': 'HTTP', 'http_status': error.code,
                        'provider_code': error_code(code, 'UNRECOGNIZED')[:64],
                        'provider_type': provider_type if provider_type in allowed_types else 'UNRECOGNIZED'}
            try:
                on_http_failure(metadata)
            except Exception:
                pass  # Observation must not change the transport exception.
        raise safe_error from None'''
    after = after.replace("        raise SafeError(error_code(code, 'http_error'), error.code) from None", replacement, 1)
    assert before != after
    compile(after, '<unapplied-observability-proposal>', 'exec')
    diff = ''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile='a/rosa-research/src/rosa_auth/oauth.py', tofile='b/rosa-research/src/rosa_auth/oauth.py'))
    (ROOT/'instrumentation/PROPOSED_HTTP_OBSERVATION_HOOK.patch').write_text(diff, encoding='utf-8')
    return dict(applied=False, target='rosa-research/src/rosa_auth/oauth.py', original_sha256=digest(path),
                proposed_content_sha256=__import__('hashlib').sha256(after.encode()).hexdigest())

def main():
    assert not (ROOT/'freeze.json').exists(), 'A blocked preparation must not present a freeze'
    rows = dev_rows()
    analysis = read(ROOT/'analysis/dev-analysis.json')
    heldout = [c for c in read(REV/'stage-1/cases.json') if c['split'] == 'heldout']
    assert len(heldout) == 38
    counts = Counter(c['kind'] for c in heldout)
    eligible = [r for r in rows if r['id'] != 'G1r1-dev-012-primitives']
    averages = {}
    proposed = {'ladder': (3, 2), 'missing_prerequisite': (3, 2), 'unavailable_source': (3, 2),
                'ambiguous': (1, 1), 'write': (5, 2), 'write_fault': (5, 2)}
    expected = 0
    for kind, turns in proposed.items():
        values = {}
        for mode, assumption in zip(('primitives', 'macro'), turns):
            group = [r for r in eligible if r['case']['kind'] == kind and r['mode'] == mode]
            actual = sum(r['inference']['calls'] for r in group)/len(group) if group else None
            assert actual is None or actual == assumption
            values[mode] = dict(dev_evaluable_trials=len(group), observed_mean_calls=actual,
                planning_calls=assumption, source='Stage 2 evaluable mean' if group else 'Prompt-provided planning assumption, not an observed dev mean')
        expected += counts[kind]*sum(turns)
        averages[kind] = dict(heldout_cases=counts[kind], by_condition=values)
    assert expected == 200
    disk = shutil.disk_usage(ROOT)
    prior_inputs = {name: digest(REV/name) for name in ('worlds.py', 'catalogue.py', 'catalogues.json',
        'prompt-contract.json', 'PREDICTIONS_AND_THRESHOLDS.md', 'SCORING_CONTRACT.md',
        'paired-order-proposal.json', 'template-groups.json')}
    prior_inputs['stage-1/cases.json'] = digest(REV/'stage-1/cases.json')
    prior_inputs['stage-2/scoring.py'] = digest(REV/'stage-2/scoring.py')
    candidates = {p.relative_to(ROOT).as_posix(): digest(p) for p in ROOT.rglob('*')
                  if p.is_file() and (p.suffix == '.py' or p.name in ('CENSORING_RULES_V1.md', 'owner-inputs.json',
                      'PRE_RUN_NOTE.md', 'AUTHORSHIP_CARRY_FORWARD_AMENDMENT_2026-11-14.md'))}
    auth = read(ROOT/'local-auth-presence.json')
    preflight = dict(status='BLOCKED_NOT_LAUNCH_READY', study='G1 revision 1 Stage 3; AI-authored cases',
        current_stage_model_allowance=0, stage4_authorized=False, freeze_created=False,
        frozen_input_hashes='NOT_AVAILABLE: no freeze', candidate_prior_input_hashes=prior_inputs,
        candidate_stage3_input_hashes=candidates, planned_heldout_cases=38, planned_heldout_trials=76,
        planned_heldout_groups=len({c['template_group'] for c in heldout}),
        planned_ladder_groups=len({c['template_group'] for c in heldout if c['kind'] == 'ladder'}),
        proposed_backend_window_seconds=28800, machine_awake_required=True,
        estimated_requests=expected, estimate_basis=averages,
        ordinary_request_cap=608, ordinary_arithmetic='38 cases x 2 conditions x 8', reserve_cap=3,
        total_physical_request_cap=611, quota='UNKNOWN; M4/G1 local ceilings and unused slots are not provider quota',
        authorization_local_presence=auth, live_provider_validity='NOT_CHECKED', renewal='NOT_ATTEMPTED_IN_STAGE3',
        zero_inference_restore_only_preflight='NOT_RUN: ordered gates and freeze are blocked; no login permitted',
        free_disk_bytes=disk.free, disk_total_bytes=disk.total,
        proposed_stage4_storage='../stage-4/ (not created)', proposed_traces='../stage-4/trials/<trial_id>/trace.json',
        phoenix_plan='Own isolated local Phoenix at 127.0.0.1:6006, fresh stage-specific storage; refuse occupied port; flush and exact local/persisted span audits; stop only owned service.',
        retry='Unchanged M4 explicit HTTP 502/503/504 only, existing code exclusions, max one retry/logical call, max three reserve, one-second backoff, charge every physical attempt. No in-stream retry or robot replay.',
        resumption_rule=DECISION5, protected_source_change_allowed=False, observed_stage3_model_requests=0)
    write('LAUNCH_PREFLIGHT_RECORD.json', preflight)
    (ROOT/'LAUNCH_PREFLIGHT_RECORD.md').write_text(f'''# Stage 3 launch preflight record — NOT LAUNCH READY

Date: **2026-11-14**. Stage 3 has a **zero-model-request** allowance. Stage 4 is not authorized.
This is a draft preflight record for owner review, not proof of a valid provider grant or a completed freeze.

## Proposed held-out batch

38 cases x two conditions = **76 Sol task trials**. There are {preflight['planned_heldout_groups']} held-out
template groups, including {preflight['planned_ladder_groups']} ladder groups. All cases remain AI-authored.
The proposed ordinary ceiling is **38 x 2 x 8 = 608**, plus **3** eligible infrastructure-reserve attempts:
**611 charged physical attempts maximum**. These local ceilings are not provider quota. Quota is **UNKNOWN**.
The proposed backend window is eight hours. Keep the machine running and awake throughout any later authorized batch.

The request planning estimate is **200**, from 24 ladder cases x5 paired calls, six writes x7,
two missing-prerequisite x5, two unavailable-source x5, two ambiguous x2 and two partial/ineffective x7.
Evaluable Stage 2 means reproduce the prompt's per-kind ratios except unavailable-source: there is no dedicated
unavailable_source dev case. Its 3/2 values are a supplied planning assumption, not measured dev behavior.
The censored primitive call is excluded from per-kind means. An estimate is not an account allowance or guarantee.

## Authentication, storage and instrumentation

Local protected research-record presence: **{auth['LocalRecordPresent']}**. Contents were not read or decrypted.
An initial sandbox-denied presence check was retained as attempt 01; its false return did not establish absence.
The metadata-only recheck succeeded. Current provider validity is **NOT CHECKED**; renewal is **NOT ATTEMPTED**.
A fresh restore-only renewal/scope/model-catalogue check, with no login or inference, remains required after the
earlier gates and freeze are ready. Previous Stage 2 authorization is historical evidence, not current validity.

Recorded free disk: **{disk.free:,} bytes**. Proposed later storage is ../stage-4/, with trial traces under
trials/<trial_id>/trace.json. No Stage 4 directory or service was created. Phoenix would use owned isolated
loopback storage, exact persisted/local span matching and normal owned-service cleanup. Authentication must
retain existing scopes and optional protected persistence, clear in-memory credentials, and never start consent.

The requested A2 HTTP metadata cannot be fully captured outside the unchanged helper. The proposed source diff
is unapplied. Zero-network boundary probes passed; integrated instrumentation validation is incomplete.

## Required resumption paragraph (verbatim)

{DECISION5}

## Owner review and authorization

No freeze exists. Candidate hashes are listed in LAUNCH_PREFLIGHT_RECORD.json, explicitly not called frozen hashes.
The ordered gate table in STAGE3_STATUS.md identifies the missing instrumentation decision, prediction definitions,
control rerun and actual independent reviews. Do not treat this draft as G-h PASS or permission to run Stage 4.
No live request, OAuth login, Git commit, upload or publication occurred during this preparation.
''', encoding='utf-8')
    diff = proposed_diff()
    write('instrumentation/proposed-diff-record.json', diff)
    gates = {
        'G-a': dict(status='PASS', evidence='owner-inputs.json; existing owner-approved AI-only amendment carried forward as option B; no teammate independence claimed',
                    unblock=None),
        'G-b': dict(status='BLOCKED', evidence='No new fixtures; prior 132 controls remain preserved, but the specifically requested fresh held-out control/audit rerun was not performed. A2 stop condition prevents advancing.',
                    unblock='Resolve instrumentation/prediction protocol conflicts, then run zero-model controls on the final mapped or unchanged AI-only case set without altering earlier evidence.'),
        'G-c': dict(status='BLOCKED', evidence='instrumentation/observability-boundary-tests.json: six zero-network fixtures passed, but HTTP provider code/type is discarded before an outer wrapper; no source edit applied.',
                    unblock='Owner review of the unapplied minimal optional HTTP-observation hook, or a documented decision to narrow the instrumentation requirement; then full subclass/golden/canary validation before a new freeze.'),
        'G-d': dict(status='BLOCKED', evidence='Censoring rules written; all 10000 bootstrap draws retained; eight analysis test methods passed; Stage 2 totals and PRE_OUTPUT class reproduced. P1-prime through P6 are undefined in supplied existing rules.',
                    unblock='Supply exact P1-prime/P6 definitions or explicitly retain existing P1-P5; finish and validate the full prospective prediction engine before freezing. Current candidate rejects held-out use.'),
        'G-e': dict(status='BLOCKED', evidence='Martin named as requested reviewer; kit and hash ready; zero actual new reviewer-authored cases/results received.',
                    unblock='A person/model other than the implementing agent authors new adversarial cases, runs the kit, reports coverage/substantive defects and records the unchanged post-review scorer hash.'),
        'G-f': dict(status='BLOCKED', evidence='Four G1 transcripts randomized/blinded; no ratings submitted. Requested owner reviewer has prior aggregate exposure; uninvolved criterion not established. M4 eight are separate.',
                    unblock='After authoring is settled, an uninvolved reviewer submits ratings and an exposure/sequencing attestation; preserve disagreements. Do not invent them under Martin\'s name.'),
        'G-g': dict(status='BLOCKED', evidence='No freeze manifest created because prior gates are not passed.',
                    unblock='Pass all earlier gates, resolve protocol changes with owner approval, then hash final inputs and verify protection.'),
        'G-h': dict(status='BLOCKED', evidence='Draft record and candidate hashes ready; provider validity/renewal not checked and frozen hashes do not exist.',
                    unblock='After G-g, perform/read the zero-inference restore-only preflight and complete the actual record. Stop for owner review and separate Stage 4 authorization.')}
    write('stage3-gates.json', gates)
    protection = check_protected()
    write('protected-check-after.json', protection)
    assert protection['pass']
    write('FREEZE_READINESS.json', dict(ready=False, freeze_created=False, blocking_gates=[g for g, v in gates.items() if v['status'] != 'PASS'],
        protected_check=protection, stage3_model_requests=0, stage4_authorized=False))
    status = ['# G1 Stage 3 status', '', 'Date: **2026-11-14**.', '',
        '**Preparation performed; freeze and launch BLOCKED. Zero live model requests. Stage 4 is not authorized.**', '',
        'All earlier artifacts remain unchanged. Stage 2 is DEVELOPMENT-ONLY evidence. This directory contains new preparation outputs, not a completed freeze.', '',
        '| Gate | Status | Evidence | What unblocks it |', '|---|---|---|---|']
    for name, gate in gates.items():
        status.append(f'| {name} | {gate["status"]} | {gate["evidence"]} | {gate["unblock"] or "Owner-approved AI-only policy retained."} |')
    status += ['', '## Completed preparation', '',
        '- A1: [audit addendum](STAGE2_AUDIT_ADDENDUM.md), unchanged raw scores and sources.',
        '- A2: six zero-network boundary fixtures, golden stream-error/eligibility comparisons and canary record checks; [unapplied proposed diff](instrumentation/PROPOSED_HTTP_OBSERVATION_HOOK.patch). Full integrated observability is blocked.',
        '- A3/A4: [analysis-only censoring rules](CENSORING_RULES_V1.md), V1/V2/V3, per-domain/depth and discordant pairs, excluded-pair counts, pair gaps, tool sequences, cost views, 10000 whole-group draws with seed 20261113, and eight passing analysis-tool tests. Candidate prediction engine is incomplete and refuses held-out use.',
        '- A5: scorer hash, empty reviewer form and execution harness. No implementing-agent review cases or invented outcomes.',
        '- A6: author packet with public catalogue/tools only, request schema, exact-text fixture-mapping tooling and empty mapping log. No teammate file was supplied.',
        '- A7: randomized four-case G1 packet, private mapping outside the packet, blank ratings/attestation and later packet generator. M4 eight cases are not included.',
        '- A8: [draft preflight record](LAUNCH_PREFLIGHT_RECORD.md), actual local-record presence and disk measurement, 200-request planning estimate, 608+3 ceiling and future service/recovery plan. No current grant or quota is inferred.', '',
        '## Audit facts and unresolved definitions', '',
        'V1: primitives 17 correct + 1 infrastructure-censored /18 scheduled; macros 18 correct /18. '
        'V2: 17/17 evaluable primitives and 18/18 macros. V3: 17/18 and 18/18. '
        'One Base depth-6 pair is excluded from matched-success efficiency. No pair gap exceeds 30 minutes. '
        'These dev views do not adjudicate held-out predictions.', '',
        'The source file defines P1-P5; the new request asks for P1-prime through P6 without supplying their definitions. '
        'The existing rule engine is diagnostic only. No new prediction is fabricated or silently aliased.', '',
        '## Owner inputs and protocol conflicts', '',
        'The owner asked to fill administrative fields and previously selected the documented AI-only fallback for this same G1 revision. '
        'Option B is carried forward with that evidence, rather than invented teammate authorship. The new template\'s UNSET placeholder '
        'is superseded by the existing owner decision and current request to fill inputs from records. All results must say AI-authored cases.', '',
        'Martin is the requested reviewer, not a recorded completed review. The independent scorer review needs actual new cases from someone '
        'other than Codex. The uninvolved clarification criterion cannot be satisfied merely by entering an owner name with prior exposure.', '',
        'A2 requires HTTP fields that the protected helper discards. The request forbids applying that source edit, so the concrete diff is '
        'presented unapplied. Approving the change would require a dated protection-policy amendment and fresh validation; it is not authorized by '
        'the broad earlier request to ignore blockers.', '',
        'The new Stage 3 instructions authorize zero inference and expressly stop after preflight. They supersede the earlier broad wish to '
        'launch held-out immediately. The standing interruption instruction allows only authorized unstarted work, never a new stage or budget reset.', '',
        '## Bias and scope', '',
        'The implementation and cases share AI authorship; exact numeric targets, explicit source allowlists, one write skill/domain and short '
        'fixed loops can favor macros or create ceilings. Native depth is not model-decision depth and covaries with fields/context/source identity. '
        'Condition wording remains confounded with architecture. Mock observer separation is not independent physical sensing. There is no stock-ROSA '
        'comparison. The near-duplicate 4b catalogue remains OFF. Human review and new held-out backend performance are not claimed.', '',
        f'Protected-file check: **PASS**, {protection["files"]} current prior files plus {protection["ancestral_files"]} ancestral protection entries checked; zero mismatches. '
        'No protected source, earlier score, report, archive or frozen input was changed. No Git commit, push or upload was performed.', '',
        'No freeze manifest or scorer-review results were manufactured. The preparation manifest (if present) is only a post-work inventory and does not pass G-g.']
    (ROOT/'STAGE3_STATUS.md').write_text('\n'.join(status)+'\n', encoding='utf-8')
    (ROOT/'SCORER_REVIEW_RESULTS.md').write_text('''# Scorer review results — NOT OBTAINED

Date: 2026-11-14. Requested reviewer: Martin. Received new reviewer cases: **0**.
Prepared kit and exact scorer hash: scorer-review/. No independent findings or defect clearance is claimed.
The eight analysis tests and six instrumentation boundary probes are development checks, not scorer review.
G-e remains BLOCKED. A substantive reviewer finding requires documented disposition and pauses launch;
any scorer change after review restarts it. No score or prior counterfactual has been relabeled as new review.
''', encoding='utf-8')
    print(dict(gates={name: g['status'] for name, g in gates.items()}, expected_requests=expected,
               model_requests=0, protected_check=protection, freeze_created=False))

if __name__ == '__main__':
    main()
