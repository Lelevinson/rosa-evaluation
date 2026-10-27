# M4 external feedback and assessment

Date: **2026-10-27**. Status: interpretation and M5 planning context only.

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

## Proposed M5 priorities, not new execution orders

1. Prepare a short claim/evidence/limitation ledger and a focused final narrative.
2. Add appropriately qualified uncertainty and paired/family-aware summaries from
   saved data, clearly labeled as post-hoc analysis rather than a changed protocol.
3. Obtain human review of the eight clarification cases; retain the existing Codex
   operator reviews and any disagreements instead of silently replacing them.
4. Check off-machine backup/publication status and package a runnable demonstration.
   Local commits are still not a remote backup. No push or new demo model calls
   are performed merely because this feedback recommends them.
5. Consider a separately scoped selection-only diagnostic only if the team needs
   an answer that changes an actual project decision. Varying wording, catalogue
   order/descriptions or reasoning adds distinct interventions and may require
   transfer checks; hundreds of related paraphrases do not establish broad autonomy.
   This diagnostic is optional and has not been authorized or started by this review.

Memory, full JTVR, hardware and a new general planner remain deferred. M5 is still
the recommended next milestone, not a new study already in progress.

The [user-supplied feedback](M4_CLAUDE_FEEDBACK_RECEIVED_2026-10-27.md) is retained
separately. For actual results use the [final M4 report](../artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md).
