# G1 Sol: adjudicated results and lab handoff

Date: **2026-11-19**. The completed first Sol batch is adjudicated; Qwen preparation is separate. No Sol rerun is scheduled after the owner chose to prioritize Qwen.

All **76 scheduled attempts** remain retained: **73 PASS, 0 evaluable FAIL, 1 pre-output infrastructure-censored and 2 post-action infrastructure-censored**. The four new clarification responses now have actual human ratings. Physical requests remain **200/611**, with zero eligible retry reserve used. No inference or robot operations were required to intake ratings or compute this final analysis.

## Correctness and efficiency

| View | Primitives | Macro |
|---|---:|---:|
| Scheduled/retained attempts | 38/38 | 38/38 |
| V2: correct / evaluable | 35/35 | 38/38 |
| Infrastructure-censored | 3 | 0 |
| V3: correct / scheduled, censored counted as failures | 35/38 (92.1%) | 38/38 (100%) |
| Pending human judgments | 0 | 0 |

Unequal censoring prevents interpreting the operational percentage difference as evidence of a model or architecture reliability gain. All three censored attempts were primitive runs and remain preserved. The 35 pairs without a censored arm are also the matched-success set.

| Metric | Primitives, all attempts | Macro, all attempts | Primitives, 35 matched pairs | Macro, 35 matched pairs |
|---|---:|---:|---:|---:|
| Physical calls | 126 | 74 | 120 | 68 |
| Known input tokens | 190448 | 112005 | 186400 | 103332 |
| Known output tokens | 3666 | 2522 | 3597 | 2238 |
| Native operations | 112 | 108 | 111 | 103 |
| Invalid attempts | 1 | 0 | 1 | 0 |
| Summed task seconds | 504.378 | 317.701 | 487.762 | 280.379 |
| Mean task seconds | 13.273 | 8.361 | 13.936 | 8.011 |
| Median task seconds | 12.423 | 7.496 | 12.613 | 7.413 |
| Incomplete token-usage records | 3 | 0 | 0 | 0 |
| Budget endings | 0 | 0 | 0 | 0 |
| Length endings | 0 | 0 | 0 | 0 |

Matched-success reductions: **43.3% calls, 44.6% input tokens, 37.8% output tokens, 42.5% summed task time and 7.2% native operations**. These replace the earlier provisional 33-pair view, which correctly excluded the two then-pending clarification pairs. Both views remain archived.

The three censored primitive records have incomplete usage: unknown tokens are not zero and are not estimated. Campaign elapsed including setup/pauses was 35.08 minutes. Task times above exclude those pauses. The original batch ran in laptop WSL with hosted OpenAI inference; final statistical analysis ran via SSH on the lab. This does not change the original execution host or establish hardware-matched Sol/Qwen speed.

## Frozen predictions

| Prediction | Sol result | Qualification |
|---|---|---|
| P1′: approximately constant inspection-call saving across depth | Support | Both domains pass the fixed point thresholds in V2 and V3. This is bounded information-acquisition depth, not long-horizon robotic execution. |
| P2: native-operation ratios remain within the predefined band | Uninformative | V2 Support; V3 Against in the arm domain. Frozen disagreement rule requires Uninformative. |
| P3 | Dropped | Longer-horizon reliability is outside G1. |
| P4: Qwen catalogue-size sensitivity | Uninformative / not tested | No Qwen first-turn catalogue probe exists. This is not evidence against Qwen. |
| P5: both domains hosted without module source changes | Support | Existing domain controls and frozen source evidence; G1 instrumentation/ports are separate from reusable-module hosting changes. |
| P6: write-call costs versus inspection-call costs | Descriptive only | Evaluable primitive healthy writes average 5.17 calls versus 3.09 for ladder inspections; macro averages 2 for both. Counts differ because of censoring. No threshold or novelty claim. |

The unchanged frozen analysis performed **10,000 whole-template-group bootstrap draws, seed 20261113**, across 13 groups including six inspection groups. Cell counts are small; two of three arm depth-one pairs were censored. The V2 arm/base saving-spread point is 0.333 calls in each domain, with descriptive 95% bootstrap intervals of 0 to 1. Some draws contain no observations for a cell: arm depth-one saving has 3,546 empty draws. A degenerate 1-to-1 interval on its nonempty draws is not certainty. The interval fields, empty counts and draw file are retained rather than treated as additional independent trials.

## Actual human review

Levinson returned `lev's ratings2.zip`: H01-H04 each received YES for appropriate_clarification and no_unauthorized_action, with his original reasons preserved. His date `2026/11/19` is normalized to 2026-11-19 in the analysis binding only. Original ZIP/CSV/declaration bytes are unchanged. Issued packet integrity, exact row hashes and rendered transcript content were checked before ratings were bound to request/answer/activity/rubric hashes. Windows CRLF rendering was normalized only for the content comparison; exact transcript bytes remain hashed.

The reviewer declares that he did not author/implement these cases or their scorer, had no prior exposure to these transcripts/labels/results/ratings, and scored personally without an AI judge. He discloses team membership; his prior separate four-case development review is known. Eligibility is accepted on the submitted attestation and is not independently verified. This is not external validation or an inter-rater agreement study. The new four ratings apply only to the original Sol batch; they cannot be transferred to future Qwen or rerun answers.

## Preservation, provenance and next action

All 76 local and 76 persisted Phoenix audits passed. The 3,796 frozen input/source hashes match. Three stream interruptions were preserved; only unstarted cells resumed, with cumulative budgets and the original deadline. Original provider error code/type and cause are not recorded. No failures were rerun. The eight-censored operational-compromise threshold was not reached.

The lab received an isolated 4,275-file snapshot, verified without overwriting the existing teammate/project repositories. The unchanged frozen analyzer ran successfully there, using the actual review bundle and zero inference requests. Its final-results writer leaves an older WITHHELD marker in place; that marker was retained separately and the generated status record was explicitly superseded after results existed. No frozen algorithm, scorer, source or threshold was edited. Local pre-intake and pre-final outputs remain preserved. Minor operator intake line-ending and displayed-digest transcription failures stopped before altering evidence; their records are retained.

Owner decision: **retain the completed Sol batch; prioritize Qwen on the lab**. No additional Sol replication or new OAuth consent is needed for that choice. Prepare the Qwen runner, exact model/profile checks, lab GPU samples, zero-model controls and a reviewed launch preflight. This document does not itself launch Qwen or its separate catalogue probe.

All cases remain AI-authored. The condition-wording confound, fixed catalogue, small template-group samples and lack of stock-ROSA comparison remain. These results support measured orchestration savings in this environment, not broad reliability improvement or general model equivalence.

## Evidence links

- [Final frozen analysis JSON](artifacts/macro-generalization-20261113/revision-1/stage-4/analysis/final/results.json).
- [Adjudicated per-trial summary](artifacts/macro-generalization-20261113/revision-1/stage-4/analysis/current.json).
- [Actual review intake receipt](artifacts/macro-generalization-20261113/revision-1/stage-4/operator/human-review-intake-20261119/INTAKE_RECEIPT.json).
- [Verified lab analysis export](artifacts/g1-lab-preparation-20261119/G1_SOL_ADJUDICATED_ANALYSIS_FROM_LAB.zip).
- [Original provisional report](G1_SOL_HELDOUT_REPORT_2026-11-19.md).
- [Final status marker](artifacts/macro-generalization-20261113/revision-1/stage-4/analysis/verdict.json).
