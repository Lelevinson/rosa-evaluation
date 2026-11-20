# G1-r1 pre-run proposal note

Date: **2026-11-13**. Study: **exploratory generalization study G1**.

This records the Stage0 design before any model request. Its SHA-256 is recorded
in revision-checkpoint.json and the revision manifest. Thresholds/counts/suffix/
ceilings are defaults awaiting confirmation, and independent teammate authorship
is unmet. No final experimental freeze, Stage1 control run or live request is
authorized by this preparation note.

## Rules

- Preserve all earlier protected files and the entire stopped Stage0 package.
  All new code, outputs, tests and amendments remain within revision-1.
- No changes to src/rosa, src/rosa_reliability, the old mock, historical reports
  or frozen source files. Use only the current public macro APIs. Stop and report
  if a source change is required; do not apply an extension or private-session patch.
- Record absent measurements as **not recorded**. Stage0 unit observations and
  explicitly labelled M4-based future-consumption estimates are not model results.
- Count every physical attempted request. Retain failed trials and eligible
  infrastructure attempts. Never replace trials or replay robot commands.
- Protected OAuth file presence may be checked locally, without reading tokens.
  Presence is not provider validity or quota. Future live runs may restore an
  existing grant only; no login fallback. Stop/checkpoint if authorization fails.
- No Git commit, push or upload. No background launch after this preparation.
- Each later stage requires explicit confirmation. The supplied independent
  teammate gate remains unmet by AI-authored drafts; no independent author is
  invented. Any AI-only alternative needs a stated protocol amendment before use.

## Revised design and case split

Two separately implemented mock domains, arm and mobile base. Each registers four
InspectionSkills (native depth1/2/4/6) and one StateSkill (healthy off-target
read/conditional-write/fresh-verify depth3), without extra catalogue descriptions.
Primitive inspection already batches the selected sources into one call, so its
expected3 versus macro2 model turns is constant across depths. Source metering
does not collapse d physical source attempts into one native operation.

16 dev cases and38 held-out-designated cases are proposed. Held-out cells are
24 ladder (3/domain/depth),6 movement (3/domain),8 non-depth (one missing pose,
ambiguous intent, partial/ineffective write and unavailable source/domain).
Ladder cases include true/false/unavailable observations, rather than only healthy
conditions. Every task has fresh state; no cross-trial memory/cache assistance.
Template groups, not individual cases, stay wholly within one split. Cases are
drafts, newly authored, not independently reviewed for semantic M4 novelty.

Keep the M48-call,2048-observed-output,10-native,16-attempt,3-correction,
<=1-dispatch,360-second task limits. Keep the original8-hour backend ceiling as
a proposed unchanged bound; timeouts stop progress rather than extending it.
Qwen uses A:8192 context,1024 output/call,temperature0,seed42,think=false,
original auto/effective-enabled FA andf16 KV, unchanged model digest.

The exact system prompt, RULES, condition sentences and budget/unit suffixes are
recorded in prompt-contract.json. Base-only substitution:

Original: `Joint tolerance 0.025 radians.`

Replacement: `Position tolerance 0.025 metres; fraction tolerance 0.025.`

Base heading is a fraction of one full turn, not radians. The same numerical
tolerance0.025 applies to each registered numeric coordinate in the public API;
Boolean readiness uses its existing0/1/null encoding. The substitution is applied
identically to both arms. The condition-wording confound remains.

The base write is a bounded numeric pose update with a known-pose prerequisite,
not navigation with route planning, energy guards or physical dynamics. Richer
multi-source movement prerequisites are outside this API and deferred to G2.

## Gates

0. User reviews the counts, suffix, thresholds, ceilings, observer proof and
   authorship limitation. Independent teammate gate must be met, or an explicit
   authoring amendment adopted. No inference before confirmation.
1. Structural controls first, using real public adapters and scripted/fake model
   responses. Verify actual turn counts and native sequences per skill; stop on
   contradiction before Sol dev. Exercise all fault cases; verify observer tests,
   local trace audit and persisted Phoenix exact span-ID matching. P5 requires
   unchanged source. Stage0 constructor checks alone do not satisfy this gate.
2. Confirmed Sol dev: one counterbalanced paired run/case. No prompt/guard/condition
   tuning. At most one dated case/scorer-defect amendment cycle.
3. Review dev/amendments; hash final sources, cases, scorers, budgets and thresholds;
   verify zero mismatches; obtain user confirmation.
4. Confirmed held-out:38 cases,76 trials/model; single run, no replacing failures.
   Review reserve ledger, authorization and world-state preflight before launch.
4b. Separately confirmed first-turn probe:38 cases x3 catalogue sizes(3/5/10),
   macro sentence only, each backend; no tools. Never generalize it to primitive
   wording. Ambiguity uses a frozen no-target sampler. Original Qwen A with three
   reviewed idle GPU samples/offload inventory, or separately recorded lab hardware.
5. Apply the confirmed prediction rules; show per-domain/depth/discordant pairs,
   clustered uncertainty, all-attempt/matched-success costs, native batching,
   budget/length endings, both ambiguity views and every deviation. State the
   limits of two mocks/two backends. Horizon-dependent reliability stays in G2.

Stop on source-change need, lost authorization, exhausted ceiling, changed digest,
protected-file mismatch or unmet authorship gate. Do not extend limits. No step
after Stage0 has started.
