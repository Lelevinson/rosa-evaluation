# User-supplied Claude feedback on the master README

Date received: **2026-10-27**.

The following is user-supplied feedback attributed to Claude. Its recommendations
are preserved as discussion context, not execution instructions or authorization.
It comments on the master README and is not an independently verified raw-data audit.

---

Overall this is a strong undergraduate project, but its merit lies somewhere different from where the document locates it.

## Research merit

The macro idea itself isn't novel. Skill libraries, macro-actions, tool bundling and "Python does the deterministic parts" are well-trodden ground, and your own document says so. A ~45% reduction in model requests when code does the routine steps is close to true by construction. It's nice that it replicated across four separate comparisons (46.7%, 45%, 44.1%, 47.2%), but it isn't a surprising finding.

The real merit is in two other places:

- **Evaluation rigor.** Frozen protocols, independent scoring, trace audits, preserved failures, and corrections like the Qwen 32/32 → 28/32 fix are uncommon at this level. That is your most defensible contribution.
- **The distinction between evidence truth and goal correctness.** Qwen submitted accepted, grounded SUCCESS reports for the wrong goal, five times in M4. Verification systems that check "is this report true?" without checking "is this the thing the user asked for?" have a blind spot, and you've shown it concretely. I'd make this a headline finding.

## How I read the M4 results

- **Sol's 20/20 vs 20/20 is a ceiling effect.** It "passed retention" trivially. Your tasks can show efficiency for a strong model but can't discriminate on reliability.
- **Qwen's 15 vs 14 is one trial, so it's noise.** Treating it as "failed retention" is fine as a pre-registered engineering gate, but don't present it as evidence the macro hurts. Also, with temperature 0 and a fixed seed, your repetitions aren't independent, so the effective n is below 20.
- **The macro is nearly orthogonal to Qwen's dominant failure.** All 11 failures were wrong skill selection (readiness inspection chosen for movement requests, or for ambiguous ones). That error happens before macro vs primitives matters, so both conditions suffer from it. This is your most interesting result, and the document buries it.
- **Task horizon is short.** Macros should matter most for long multi-step tasks, where primitive loops have more chances to go wrong. Your tasks take 2-4 model calls, so the design is biased toward finding little reliability difference.
- **A comparison is missing.** Both M4 conditions share your guards and report contract. You haven't shown yours versus stock ROSA on this task suite, and that's the first question an examiner will ask about "improving ROSA".

## The plan and roadmap

The scope discipline is the best part: negative results allowed, JTVR paused instead of renamed, no architecture invented per failure. The pivots (JTVR → batching → reliability → workflow → macro) were evidence-driven, and I wouldn't apologize for them. But the project has produced about ten studies under incompatible protocols, and the process has outpaced the insight. The document's hedging is honest but so dense that a reader will drown. M5 should be about narrative, not more data.

## Advice on continuing

1. **Back up first.** The doc says commits are local only. Push to `member/martin` and copy the evidence somewhere else.
2. **Write a claim ledger.** Make it one page, listing each claim you'll make and the evidence for it. The final report should be about 10 pages, with the rest as appendices.
3. **Reframe the thesis.** Something like: "Bundling deterministic steps reliably cuts model calls by roughly 45% and keeps reliability within noise. For a small local model the bottleneck is intent-to-skill selection, which neither condition addresses, and evidence-truthful reports can still answer the wrong goal."
4. **Run a selection-only diagnostic.** I'd make this one exception to "no new experiments". Skill selection needs no simulator, so you can test hundreds of paraphrased requests, vary catalogue ordering and descriptions, and compare with and without reasoning enabled. It checks whether the 11/11 pattern is a presentation artifact (the inspection skill looks like the "safe" choice) or genuine model weakness, and it gives you a sample size that supports real statements. It's a diagnostic, not a new architecture.
5. **Add proper statistics.** Report confidence intervals (Wilson for pass rates, bootstrap over pairs for call reduction) and a paired test. This costs nothing and makes the tiny samples honest.
6. **Get human eyes on the eight clarification transcripts.** Right now they were reviewed by the same assistant that built the system. Read them yourself, and have a teammate re-score a sample.
7. **Record a demo video** of the M3 demo with both backends. It's the most persuasive deliverable per hour spent.
8. **Skip memory, JTVR and hardware.** Put multi-skill chaining and stock-ROSA comparison under "future work" unless you have spare time.

Make sure you can explain every headline claim in plain words without the document open, since a viva will test that, not the audit counts.

If it would help, I can draft the one-page claim ledger or the selection-only diagnostic design.
