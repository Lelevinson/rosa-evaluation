# Independent review of G1 human clarification scoring v2

Date: 2026-11-19. **PASS for the exact effective analysis layer and trusted-input contract inspected here.** No substantive reachable defect was found in this bounded review. This does not clear the preserved legacy scorer by itself, establish general scorer correctness, authorize held-out execution, or approve the separate metadata amendment.

The reviewer is a separate AI agent, configured by the orchestrator as `gpt-6-astra`, effort `high`, with `fork_turns=none`. The parent supplied those exact spawn settings during this review; hidden runtime model identity was not independently attested. This is independent AI review, not human adjudication or independent authorship of the study cases.

## New tests and discrepancies

The reviewer authored **65 first-run cases: 63 expectations matched and 2 mismatches remain preserved**. A separate supplement added **2 correctly isolated repeat cases, both matched**. The total is 67 authored cases, with 65 matched results and 2 reviewer authoring errors. Do not describe the first run as 65/65 or erase its discrepancies.

The two first-run `authorized-repeat-*` expectations were wrong for their serialized inputs. My test accumulator retained the same mutable row subsequently used for a forbidden-repeat case. The later request sentence, `There shall be no additional acquisitions.`, therefore appeared in both serialized inputs before execution. The scorer correctly returned FAIL. This was a reviewer shared-reference construction error, not a scorer defect. The original harness, exact inputs, expectations and first-run results remain unchanged. The supplement creates separate four-source repeat inputs, changes the latest observation/reference consistently, and records all eight native acquisitions; both domains pass. These are source-based counterfactuals, not fresh runtime replays. Their constructed activity timestamps and trace identifiers are not new measured telemetry.

All expectations and exact row/bundle inputs were written before their respective executions. The implementer's tests were inspected but not rerun as this independent review. The prior review report was read to understand known negative findings; its original submission files were **not read to author cases or replayed**. Old review artifacts were hashed solely for integrity. A preliminary read-only fixture inspection found no `unavailable_source` kind in the 36 dev records and raised StopIteration; the new UNKNOWN tests use actual missing-prerequisite records instead. This was not a scorer test failure.

## Behavior observed

| Required behavior | Fresh review result |
|---|---|
| Punctuation and keyword semantics | Eight fresh answers, including `???`, Unicode punctuation, irrelevant questions, keyword negation and an imperative, remain pending without ratings. No punctuation-only semantic pass. |
| Rating interpretation | Simulated YES/YES allows the targeted imperative; NO fails; CANNOT_JUDGE remains pending unless either rating is NO. These inputs are explicitly marked synthetic, never counted as human evidence. |
| Structural action bounds | Positive simulated ratings cannot override attempted tool use, native-only records, operation-only records, prior observer dispatch, selected skill, write counters, rejected reports or unreferenced observations. |
| Runner requirements | Audit failure, actor-only truth acceptance, runtime error, timeout and recovered-failure flags each prevent PASS despite simulated YES/YES. |
| Intake/content binding | Changed answer, observer timestamp or cost invalidates an existing binding. Duplicates, orphan review rows, wrong rubric, non-Boolean eligibility, missing ratings, absent provenance and invalid dates are rejected. Duplicate trial rows are rejected. |
| Missing/malformed evidence | Incorrect earlier observer domain, Boolean dispatch count, null tool list and absent audit fail closed by exception. |
| Pending analysis | All 36 attempts and 60 primitive/34 macro calls remain included without ratings. Four semantics are pending, final verdict readiness is false, and projection to the old Boolean analysis refuses pending rows. A structurally failed row with unresolved semantics still withholds the campaign verdict. |
| Infrastructure | The actual interrupted dev row is pre-output censored, distinct from missing human review. Explicit synthetic transport chronology distinguishes pre-output and post-action censoring; human semantics become NOT_EVALUABLE. |
| Nonambiguous goals | Truthful readiness SUCCESS for a requested movement goal remains a primary FAIL with the wrong-goal flag. |
| Unsupported/stale evidence | Nonexistent report references and obsolete after-write evidence fail. Two actual UNKNOWN records remain correct; changing their status to SUCCESS fails. |
| Authorized repeats | Both new complete four-source repeat constructions pass with eight retained actor/native records. Explicit no-additional-acquisitions cases fail. |
| Existing actual human review | All four returned ratings, reasons, content bindings and submission/CSV/declaration/transcript hashes match retained sources. The issued rubric digest matches. Four actual reviewed passes remain distinct from synthetic review inputs in review artifacts. |
| Old-analysis bridge | Actual complete projection preserves inference, native records and task time. Existing V2/V3 prediction point metrics agree before/after on these dev data; this is a compatibility check, not prediction adjudication. |

## Exact trust boundary and future use

`validate_bundle` validates record structure, exact digest values and eligibility assertions. It **does not retrieve the bytes named by provenance digests, authenticate a person's identity, verify human independence, or decide whether the supplied rating actually came from a human**. Its caller is a trusted organizer supplying documented submissions and sealed complete trial records. A well-formed fabricated organizer bundle can produce REVIEWED_PASS; fresh case `trusted-organizer-can-supply-false-rating` demonstrates this deliberately with an obviously unsuitable answer. That case is labeled `SYNTHETIC_TEST_ONLY`, not a new human judgment. Treating this API as an untrusted rating-upload endpoint would violate the reviewed contract and invalidate this clearance.

The four-case binding utility supports only the actual retained submission. It compares original ZIP/member hashes and the exact normalized rendered transcript with the retained request, answer and activity counts, then binds the full canonical row and rubric. The declaration remains a real self-attestation, not independent verification of identity or every eligibility statement. The independent check here verified the retained actual bundle's hashes, ratings, reasons and full-row bindings; it did not invent another human review or rerun the binding utility to overwrite its artifact.

Future use needs its own blinded packet, actual returned declaration/ratings, organizer verification of the submitted bytes and exact content, and a new bound bundle. Four current ratings do not generalize to future transcripts. Synthetic bundles in this review must never be fed to campaign analysis as actual ratings. Caller-controlled rubric digests must be compared with the frozen issued rubric, not merely accepted because they are well-formed.

`summarize` accepts the authoritative schedule and explicitly withholds readiness when results are unstarted or semantics are pending. `project_complete_rows` enforces complete semantic adjudication for the rows it receives, **but has no schedule argument and is not itself a schedule-completeness gate**. It returns rows, not a campaign verdict. Future orchestration must check the scheduled summary before passing projected rows to prediction analysis. The development wrapper uses the actual plan and labels its outputs retrospective/dev-only; its successful point-metric comparison does not integrate or authorize a future held-out pipeline. Existing held-out/freeze gates remain necessary.

## Retained legacy limitations

The effective scorer continues to trust program-owned numeric evidence and acquisitions for nonambiguous tasks. The fresh `legacy-forged-empty-evidence` probe returns PASS after an artificial empty-evidence mutation. This reproduces a known defense-in-depth weakness at a trusted-record boundary, not a reachable model-input attack under the inspected public interface. `ReferenceReportArgs` permits status and observation ID, and `report_reference` fetches values from the latest task-local observation; `_CapabilitySession.read` creates the acquisition/evidence list from registered checks. Models cannot directly supply an empty evidence array, fabricated acquisition IDs or arbitrary numeric report payloads through that interface. No runtime replay was used to prove these source-based reachability judgments.

The unchanged legacy scorer's known defects are not erased. A change that lets callers submit arbitrary program-owned evidence, ratings, schedules or censoring annotations without organizer validation would require a new review. The independent outer runner checks are preserved; malformed trusted records may raise rather than return a friendly status, which is fail-closed behavior rather than a semantic PASS.

## Integrity and reproduction

All **66 recorded input files** were byte-identical before/after the first run and after the supplement. They include 36 retained result baselines, effective scoring/intake/development code, old scorer/runner/worlds, analysis/censoring/prediction dependencies, actual human submission artifacts, public reference/capability sources and prior independent-review artifacts. Detailed digests are in `source-hashes-before.json`, `source-hashes-after.json` and the supplement result. No implementing-agent/operator edits occurred: `operator_edits: []` throughout.

Key effective source digests:

- `adjudication.py`: `4a709cf4d4e3298bdb4587036bdfc271add768a4d50afd9de9307384f8037acf`
- `bind_existing_review.py`: `2e92b83bf45cabbb50f842a9687fe882b695445123387394d172805b3c814b21`
- Preserved `stage-2/scoring.py`: `90b0edd6d898ac749d121de29197a669593e022160503414413e0126766e8e4d`

Review execution used Python standard-library imports and local records only. **Zero model/provider requests, OAuth actions, robot operations or Git actions** were performed by the review harness or reviewer tools. The independent AI reviewer interaction itself is not counted as an experimental provider request. All new files were written under this `independent-review` directory.

Commands executed from the workspace root:

```powershell
python -B rosa-evaluation/artifacts/macro-generalization-20261113/revision-1/stage-3/clarification-scoring-v2-20261119/independent-review/review.py
python -B rosa-evaluation/artifacts/macro-generalization-20261113/revision-1/stage-3/clarification-scoring-v2-20261119/independent-review/repeat-supplement.py
```

Both scripts intentionally refuse to overwrite existing results. Reproduction requires a fresh copied review-output location with equivalent parent paths or an explicitly versioned harness; do not delete the original review artifacts to rerun them.

**Disposition: PASS for the exact effective v2 scorer within the documented organizer/program-owned-record trust boundary.** The legacy review remains failed as a historical artifact. This renewed clearance concerns the first authorized repair only; the metadata/observability gate and final freeze/launch decision remain outside this review.
