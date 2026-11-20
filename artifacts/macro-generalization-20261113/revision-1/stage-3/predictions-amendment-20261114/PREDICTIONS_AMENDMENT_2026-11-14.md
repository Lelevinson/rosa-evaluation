# G1 pre-freeze prediction amendment: P1-prime through P6

Date: **2026-11-14**. Owner-supplied definitions and confirmed interpretations. No held-out model results exist.

This amendment resolves the missing-definition finding in the earlier Stage 3 preparation checkpoint. The earlier prediction table, scripts, dev outputs and 62-file preparation inventory remain unchanged. This file and its new analysis component are candidates for the eventual G-g freeze, not a freeze or a launch authorization.

## Adopted definitions

| ID | Endpoint | Support | Against | Otherwise |
|---|---|---|---|---|
| P1′ | Sol primitive-minus-macro calls per inspection task, matched-success pairs, at native depths 1/2/4/6 | Every depth mean in [0.5,1.5] calls; maximum-minus-minimum depth mean <=0.5 | Any depth mean outside [0,2], or depth spread >1.0 | Uninformative, including missing depth cells |
| P2 | Native-attempt macro/primitive ratio at each depth | Every depth ratio in [0.75,1.25] | Any defined depth ratio outside that band | Uninformative for missing/undefined comparisons; zero primitive denominator is not imputed |
| P3 | Horizon-dependent reliability | DROPPED | Not applicable | Deferred to G2 |
| P4 | Qwen first-turn selection accuracy versus catalogue size | No accuracy fall >=0.20 between a smaller and larger tested catalogue | Any accuracy fall >=0.20 | Uninformative for missing or incomplete paired probe records |
| P5 | Hosting both mock domains through the module without required hosting-source changes | Both domains' full controls pass with zero required hosting-source changes | A hosting-source change is required; report the diff | Uninformative if controls/evidence are incomplete |
| P6 | Primitive write-skill calls compared with inspection calls | Descriptive only: report means/counts by kind and condition | No threshold or Against verdict | No invented inferential claim |

The owner confirmed: **P1′ and P2 must pass separately in both domains**. Pooled figures are supplementary and cannot override a failing or uninformative required domain. The owner also confirmed **P4 is Against at exactly a 20-percentage-point accuracy fall**, resolving the supplied Support/Against overlap. Catalogue sizes remain the existing **3,5,10**; this does not authorize 6/12 or the optional near-duplicate catalogue.

P4 reports all ordered smaller-to-larger contrasts (3→5, 3→10, 5→10) and uses the worst fall; it does not select the favorable contrast after seeing results. Accuracy fall equals the increase in error rate, in percentage points rather than relative percent. Exact fractions determine threshold equality. These are point-estimate engineering rules; whole-template bootstrap intervals remain reported as uncertainty descriptions and are not silently substituted for the newly supplied thresholds.

## Censoring, scope and denominators

P1′ includes depth-analysis ladder cases only and matched-primary-success pairs; print counts for every domain/depth. Exclude any pair containing a censored arm. P2's primary V2 compares paired evaluable cases at each requested depth, retaining native attempts even for an evaluable model failure. Its V3 includes the actual native attempts from censored trials as an explicitly labeled sensitivity view. Undefined ratios remain undefined. Also report all-attempt and matched-success costs separately.

Primary statuses follow V2. Any V2/V3 status disagreement yields Uninformative. Eight censored trials in a planned 76-trial backend run trigger operational compromise and Uninformative formal prediction statuses, under the existing decision. Incomplete schedules cannot support completed-campaign verdicts. P3 stays dropped and P6 stays descriptive rather than being misrepresented as tested hypotheses.

P6 keeps healthy writes, partial/ineffective writes and missing-prerequisite cases separate. A missing-prerequisite request may invoke the state-change skill without dispatching a command. Do not call all such cases healthy movement or pool them selectively to enlarge a gap.

P5 concerns changes needed to **host the domains**, which is distinct from the proposed authentication-observability hook. The current hook is unapplied. If approved later, the campaign must disclose that source change and amend the protection policy; it must not claim zero overall source edits. New full control completion remains a gate, and the current historical controls do not fabricate a fresh rerun.

## What this replaces and what it does not

The old P1 fractional-call-saving threshold is replaced by P1′ absolute calls saved across depth. Old P2 correctness noninferiority is replaced by native-operation equality. Old catalogue-size P3 becomes the Qwen-focused P4; longer-horizon reliability is explicitly deferred. Old P4 fractional depth-equivalence is replaced by the new absolute P1′ endpoint. P5 remains the hosting/source-change question, and P6 is descriptive. Earlier records retain their original identifiers and verdict restrictions; they are not retrospectively relabeled.

Stage 2 remains DEVELOPMENT-ONLY. Running this new component on its records validates arithmetic and missing-data handling; it is retrospective dev analysis, not preregistration of already observed data or a new prediction verdict. No prompts, weights, serving settings, scorer, cases, retry rules, budgets or permissions change here. No source hook is approved by supplying these prediction definitions.

Other Stage 3 blockers remain: instrumentation disposition, fresh controls, actual adversarial scorer review, uninvolved clarification review, freeze and current restore-only preflight. **Stage 4 remains unauthorized.**
