# Using the versioned clarification layer

This is an evaluation repair. No robot tools, agent prompts or OAuth code are
changed. The original Stage2 scorer and original reports remain authoritative
historical artifacts; this folder contains a separately labeled dev overlay and
a candidate effective scorer for the next approved freeze.

## Real data versus software fixtures

`LEV_ACTUAL_REVIEW_BOUND.json` contains only Levinson's four actual submitted
ratings. `bind_existing_review.py` verifies the original returned archive,
preserved CSV/declaration, issued packet manifest, mapping, exact request/answer
rendering and recorded activity counts before binding. Its output and original
submissions are retained, not overwritten. Dates are normalized only in derived
records; the actual submitted spelling, date format, encoding and bytes remain.

Tests explicitly named `SYNTHETIC_TEST_ONLY` simulate valid/invalid reviewer
records to exercise the validator. They are never appended to the real bundle,
counted as human judgments or used to adjudicate development performance.

The review input is organizer-controlled. Required eligibility is a real human
attestation; the software validates its representation, not the person's identity
or honesty. Hashes detect content mismatches and bind the exact input; they do
not authenticate who signed a judgment. Model output must never be accepted as
an organizer review bundle. Future actual submissions require equivalent intake
and preservation; the four development labels cannot be reused on changed rows.

## API for later analysis

`adjudication.adjudicate(row, bundle, rubric_sha256)` produces an explicit
`primary_status`, nullable `primary_correct`, semantic judgment and separate
structural/runner checks, preserving the old score and diagnostic regex result.
It rejects invalid supplied reviews and incomplete required evidence.

`evaluate_dataset` additionally rejects orphan review IDs and duplicate trials.
`summarize` retains every attempt and its costs, reports unstarted/censored/
pending/failed outcomes separately and withholds a final verdict if required
human semantics or scheduled results are missing. It does not issue prediction
verdicts, declare backend readiness or bypass original uncertainty rules.

**Do not cast pending strings to bool or hand them to the old analyzer.**
Use `project_complete_rows` first: it refuses unresolved human judgments, creates
in-memory copies and substitutes effective booleans only after adjudication.
The original censoring, paired analysis, prediction rules, uncertainty gates and
resource accounting then remain applicable. Censored original rows are retained;
the unchanged analysis classifier continues to mark them NOT_EVALUABLE. No
pending-human state is reclassified as provider infrastructure failure.

The retained dev validation exercises this bridge against the existing V2/V3
prediction point functions. It produces no held-out or final research verdict.

## Reproduce checks without overwriting evidence

From the workspace root:

```powershell
C:\Python314\python.exe -B -m unittest discover -s rosa-evaluation/artifacts/macro-generalization-20261113/revision-1/stage-3/clarification-scoring-v2-20261119 -p test_adjudication.py -v
```

The one-shot binding and development-validation scripts deliberately refuse
existing output paths. Preserve the retained outputs rather than rerunning
artifact-producing scripts over them.

No new inference, login, consent, Gazebo or physical action is part of these
checks. Metadata G-c, protection-scope disposition, freeze, launch preflight and
separate held-out authorization remain independent requirements.
