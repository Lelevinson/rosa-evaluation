# G1 Stage 2 confirmation and launch conditions

Date: **2026-11-14**. Owner authorization: run and review the fail-closed
preflight, then start Stage 2 if it passes. This authorizes **Sol dev only**.

This is the AI-authored exploratory G1 study. No independent teammate authorship
or semantic-novelty review was obtained. Preserve all earlier evidence and
protected sources, including the complete sealed Stage 1 package.

## Confirmed design and resource bounds

- **18 dev cases, 36 task trials**, one adjacent paired run per case. Alternate
  the first condition. Fresh world, agent history and task-local evidence per trial.
- **291 charged physical inference attempts maximum**: 18 x 2 x 8 ordinary
  decision slots, plus at most 3 eligible infrastructure-reserve attempts.
  This is a worst-case cap, not expected consumption or provider quota.
- Corrected M4-based planning estimate: 18 x (3.4 + 1.9) = **95.4 (~95)**
  requests. The earlier ~85 estimate used 16 cases. This remains a projection,
  not a promise; source depth, task mix and live behavior can change it.
- Existing task limits: 8 logical model decisions; 2048 observed generated
  tokens; 10 native operations; 16 tool attempts including program-owned nested
  tools; 3 corrections; at most 1 dispatched movement; 360 seconds. Read-only
  and ambiguous permissions permit zero movement dispatches. Backend ceiling:
  8 hours. Sol retains its existing serving behavior; the observed-output gate
  is not a new provider-side generation cap.
- Reserve: explicit HTTP 502/503/504 only, with the existing auth/scope/token/
  grant/client/quota exclusions; at most one retry of a logical inference,
  at most 3 reserves across the batch, 1-second backoff. Every attempt is charged
  and retained. No robot command or whole task is replayed. Unknown failed-call
  usage remains unknown, never zero.
- Later proposed caps remain **611 per backend for held-out** and **117 per
  backend for Stage 4b**. Those stages are not authorized by this confirmation.

## Confirmed thresholds

Use the original revision-1 P1-P5 definitions and whole-template-group analysis
defaults, with the following explicit confirmation/qualification:

| Item | Confirmed rule |
|---|---|
| Native operations | Macro/primitive inspection native-attempt ratio must lie in **[0.75, 1.25]**, separately at each depth in each domain. Report actual repeated acquisitions, including failures. This is a retention/accounting threshold, not a native-operation saving claim. |
| P1 | At least 20% call saving and lower 95% cluster-bootstrap bound >0 in both domains, in all-attempt and matched-primary-success views; minimum 4 matched-success pairs/domain. Against if a domain's upper bound <=0 with the minimum sample. Otherwise Uninformative. |
| P2 | Five-percentage-point loss margin retained. Against if an upper 95% delta bound <-0.05 in a domain, or any macro dispatch violation. **No Support conclusion for this small study; otherwise Uninformative.** This is a conservative reporting restriction, not a claim that a small-sample bootstrap can never numerically clear a margin. |
| P3 | First-turn error(10)-error(3) >=0.10 with lower 95% bound >0 for Support. Against if upper bound <=0 with non-ceiling/floor variation. Otherwise Uninformative; also show size 5. Macro wording only. |
| P4 | Entire 95% depth-6 minus depth-1 call-saving interval within [-0.10,+0.10] in both domains, with at least 2 matched-success pairs per required cell. Entire interval outside that band in a domain is Against. Otherwise Uninformative. |
| P5 | Full unchanged-source Stage 1 execution, observer, fault and local/persisted trace controls passed. Do not infer model performance from this engineering result. |

Analysis defaults for later confirmed evaluation remain 10,000 whole-template-
group bootstrap draws, seed 20261113, percentile 95% intervals, no pooled
p-values, actual denominators and degenerate/empty draws disclosed. The held-out
ladder has **6 template groups**, not 13 independent ladder groups.

**Stage 2 does not adjudicate P1-P4.** Its 18 cases check live scoring, budgets,
trace completeness and actual execution paths. A model deviating from scripted
3-versus-2 inspection turns is a recorded observation, not grounds to repair its
instructions, replace a trial, or discard the result.

## Exact Base tolerance suffix

The unchanged full suffix is:

```text
Limits: eight charged model calls, 2048 observed generated tokens, 1024 local tokens per call, ten native acquisitions/commands, sixteen tool attempts, three corrections, 360 seconds and at most one movement dispatch. Position tolerance 0.025 metres; fraction tolerance 0.025.
User: 
```

The Base-only substitution remains exactly **`Position tolerance 0.025 metres;
fraction tolerance 0.025.`** Heading is a fraction of a full turn, not radians.
Arm tolerance remains 0.025 radians. System text, RULES, both condition sentences,
catalogues, permissions and runtime guards remain unchanged.

## Authorization preflight and stop policy

Use the existing protected refresh credential and OAuth validation/renewal
implementation. Restore only: **no new consent, browser, interactive fallback or
scope expansion**. Force real provider renewal, validate the unchanged granted
scopes and renewable permission, and make an authenticated model-catalogue read
confirming gpt-6.1-sol. This uses zero inference requests. File presence is not
authorization. Provider inference quota remains **unknown** even after that read.
Review the credential-free preflight output before launch. Recheck the same
restore/model permissions at launch; checkpoint and stop on unavailable grant,
quota, resource ceiling, protected-file mismatch or failed mandatory trace audit.

Preserve the remembered encrypted credential on normal cleanup and clear tokens
from memory, using the existing opt-in policy. No credential enters artifacts,
logs, Phoenix, command arguments or Git. Existing invalid-grant cleanup applies.

## Development and later gates

No prompt, guard or condition tuning on dev results. At most **one dated case or
scorer-defect amendment cycle** is permitted; retain prior versions and outcomes.
No automatic replacement of failed tasks. Distinguish selection, evidence truth,
task contract, physical outcome, errors, budget endings and infrastructure recovery.

Same-domain near-duplicate distractors are a **possible later Stage 4b amendment**,
not added now. They need a defined sampler/catalogue freeze and later confirmation;
the current cross-domain distractor limitation stays visible.

Qwen's later Stage 5 launch needs the frozen GPU-idle preflight and reviewed
samples/settings/digest before inference. No Qwen run is authorized or started here.
