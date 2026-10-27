# M4 external feedback and assessment

Date: **2026-10-27**. Status: interpretation and M5 planning context only.

Subsequent status: the user explicitly authorized M5 execution. The live
[master record](../PROJECT_MASTER_README.md) now tracks completed work, deferred
human review and pending evaluation-publication approval. The planning discussion
below records the earlier handoff and is not the current execution status.

The user supplied a response attributed to Claude after sharing the master README.
This records that feedback and our assessment; it is not an independent audit of
the raw evidence. Attached recommendations are discussion material, not permission
to push repositories, spend model quota, enable reasoning or launch experiments.
M4 remains closed; its frozen protocol, scores and evidence archives are unchanged.

## Points to emphasize in the write-up

- The reusable bounded macro is an engineering approach; algorithmic novelty has
  not been established. Demonstrating reduced calls alone is a limited contribution.
  Actual latency, token/native work, correctness and failure coverage remain useful
  measurements because retries and failed selection can erase expected savings.
- The clearest substantive failure is the gap between grounded selected-skill
  evidence and correct user intent. Qwen produced five accepted readiness SUCCESS
  reports for wrong/unresolved goals in M4. The report validator does not establish
  unrestricted natural-language intent correctness. This deserves headline treatment.
- Trace integrity and preserved failures support credibility, but span counts are
  not themselves a reliability benefit or a novel research algorithm.
- The experiment controls routine execution ownership against a shared repaired
  ROSA reference. It does not establish superiority to unmodified upstream ROSA.
- A concise claim ledger and final narrative should make these distinctions easier
  to explain, with the extensive history/raw evidence kept as supporting material.

## Qualifications and disagreements

1. **15/20 versus14/20 is inconclusive, not established noise.** Qwen failed the
   prospective no-greater-failure engineering screen. That is not proof the macro
   harms reliability, and the small sample also does not establish equivalence,
   noninferiority or reliability preservation. Do not adopt the proposed claim
   that reliability was kept "within noise."
2. **Sol's20/20 versus20/20 cannot demonstrate a reliability gain.** It does show
   observed call/time savings with no observed correctness loss on this suite;
   unseen-task reliability remains uncertain. Passing an engineering gate is not
   a population-level reliability guarantee.
3. **Selection is a shared observed failure location, not a proven independent
   cause.** All11 Qwen failures selected inspection; seven were explicit movement
   requests and four required clarification. Both modes still delegate selection
   to the model. However, condition instructions already differ before selection,
   and later recovery differs, so this study does not prove execution architecture
   cannot affect the choice. Catalogue order/descriptions, task interpretation,
   one-skill commitment and backend capability are hypotheses, not established causes.
4. **Historical savings are not four independent replications.** They include
   different protocols, backends and successful-pair subsets from a shared code/task
   lineage. Do not pool them into a single success rate or general45% effect.
5. **Uncertainty analysis must respect pairing and task-family clustering.** Two
   repetitions with fixed serving settings are not20 independently sampled task
   families. Simple independent-binomial intervals or a naive20-pair bootstrap can
   overstate evidence. A paired/family-aware descriptive analysis can be added as
   labeled postprocessing without changing the frozen gate or old scores.
6. **Longer-horizon benefit is a hypothesis.** Current tasks are bounded single-skill
   invocations; Qwen used up to eight charged calls. The study does not establish
   that longer tasks would improve the macro's reliability advantage.

## Consolidated M5 priorities after the further Claude/ChatGPT discussion

The user subsequently supplied a [recap of the discussion](M5_REVIEW_DISCUSSION_RECEIVED_2026-10-27.md).
The four gates below consolidate that feedback; M5 execution has not started.
No quoted recommendation constitutes new authorization for remote publication,
model requests or a new study.

| Gate | Work and exit evidence | Current status |
|---|---|---|
| 1. Protect the work | Credential-check intended source/history/evidence, verify the destination and branch, and establish an off-machine copy of source, archives and checksums. | Local member/martin commits and verified ZIPs exist. No off-machine backup is verified in this session; no push is performed by processing this recap. |
| 2. Review existing failures | Compare the four Qwen partial-command records: actual model-visible prompts/tool descriptions, initial selection, feedback, native dispatch and outcome. Prepare the eight clarification cases for independent human scoring and preserve disagreements. | Outcome summaries/snapshots and some prompts have already been inspected; a deeper comparative first-turn review remains outstanding. Eight Codex operator reviews are complete; independent human review is not. |
| 3. Finalize claims and analysis | Present the ten-family table, paired wins/losses, both efficiency views and a concise claim/evidence/limitation ledger. Add only appropriately qualified exploratory uncertainty. | The M4 report already has family results and paired counts. A concise final ledger and additional family-aware uncertainty analysis remain future work. |
| 4. Package and present | Consolidate the existing module/installation instructions and limits, a clearly attributed recorded demonstration and a focused report with technical appendices. | The module and M3 demo work; no final presentation package or recorded-video completion is claimed. No new demo inference is launched by this recap. |

### Forensic expectations and provenance

Hypothesis for deeper review: describing immediate execution in macro mode may
make readiness inspection appear an attractive preliminary action, while primitive
mode may elicit direct movement selection. Look for the actual condition wording,
tool schemas and first selection; also inspect competing interpretations and
subsequent feedback. A model explanation, if present, is supporting evidence,
not privileged access to its causal reasoning. A selection difference alone
does not isolate its cause. Inconclusive traces must remain inconclusive.

These expectations are recorded **after M4 results and some snapshots/prompts
were already seen**. They are a retrospective analysis plan, not preregistered
predictions or a blind discovery. Do not claim the four trial outcomes were unseen.
Both conditions commit to one skill; the macro additionally executes its routine
immediately. Commitment is not a macro-only property.

### Corrections to the proposed final thesis

- Say savings in **model orchestration**; native work did not uniformly stay flat
  or increase. Sol had38→40 native operations (+5.3%); Qwen50→48 (-4.0%) across
  all attempts, and31→29 (-6.5%) on both-pass pairs. Different work/failures limit
  what those counts mean. Do not pool backends to hide that distinction.
- All11 failed Qwen tasks selected inspection. Only five ended with accepted
  grounded readiness SUCCESS reports; the other six ended with safe error output
  after truncation or validation-retry exhaustion. Do not call all11 false success
  reports or claim that every failed trial completed a report.
- Matched-success costs describe the subset where both modes succeeded; they
  exclude discordant/harder cases. Report them alongside all-attempt costs and
  correctness, without replacing either view or retuning the frozen primary screen.
- Plain Wilson intervals are illustrative binomial references, not a guaranteed
  lower bound on uncertainty or proof that reliability is preserved. Pairing,
  repeated cases and family clustering need explicit treatment. Fixed seed/settings
  do not provide independent coverage of20 task families.
- The absence of stock-ROSA comparison limits claims about superiority over
  untouched upstream ROSA or the whole accumulated repair bundle. It does not
  invalidate the narrower within-ROSA comparison against a shared repaired
  primitive reference. Narrowing the claim can be preferable to starting a study.

### Optional experiment boundary

A stock-ROSA comparison or small selection diagnostic is future work unless a
specific unresolved question materially affects an actual engineering decision
or necessary claim. Neither is automatically required to close M5. Any diagnostic
needs its own frozen cases, interventions, scoring and budget. Presentation
sensitivity would not establish a general model-capability explanation. No
reasoning-enabled rescue, router/planner, backend migration or hardware expansion
is authorized by this recap.

Memory, full JTVR, hardware and a new general planner remain deferred. M5 is still
the recommended next milestone, not a new study already in progress.

The [user-supplied feedback](M4_CLAUDE_FEEDBACK_RECEIVED_2026-10-27.md) is retained
separately. For actual results use the [final M4 report](../artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md).
