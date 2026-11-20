# G1 clarification scoring v2: approved repair, before held-out evaluation

Date: **2026-11-19**. Owner direction: **"okay lets handle the frist one"**, in
reply to the concrete recommendation to make human judgments authoritative for
clarification, preserve old scores, validate the revised layer and obtain renewed
independent scorer review. This authorizes that first repair and its zero-model
checks. It does not approve the second, reduced-error-metadata amendment or a
held-out launch. No special word such as "approved" is needed when the instruction
clearly authorizes the work.

This explicitly approved additional pre-freeze amendment supersedes the prior
decision to discuss this first repair before implementation. The old one-cycle
amendment allowance is not treated as automatic permission. This is a known-
defect repair informed by dev data and review, not preregistration of those data.

## Scoped five-question preflight

1. **Closest mechanism / change (F/P):** the unchanged Stage2 scorer uses a
   question/keyword regex plus a no-action check. The ordinary alternative is
   human rubric scoring. This layer makes actual eligible human ratings
   authoritative for ambiguous-intent semantics, retains the regex as diagnostic,
   and adds exact content binding and explicit pending states. This is an
   evaluation repair; no algorithmic novelty or efficiency benefit is claimed.
2. **Need / denominator (F):** the preserved separate Astra review authored41
   adversaries; six reachable clarification mismatches (five false positives,
   one false negative) block clearance. Levinson's real four-case dev review
   rates both criteria YES in all4. Four successful examples cannot validate
   the regex against those adversaries. No held-out outcomes exist here.
3. **Decision / discriminator (P):** given trusted complete trial records, a
   fixed rubric digest and an optional verified human rating, emit explicit
   PASS, FAIL, PENDING_HUMAN_REVIEW or infrastructure-censored status. A rhetorical
   question without a rating receives no semantic pass. A targeted imperative
   clarification can pass with real human adjudication. Any prohibited action
   fails even if both human columns say YES. Wrong/missing/duplicate bindings
   are rejected or pending, never inferred. No model is a human reviewer.
4. **Fair controls (P):** same rule for both domains, modes and models. Preserve
   all existing prompts, budgets, cases, retry/censoring rules and runtime. No
   human label or scorer answer is sent to the model. Non-ambiguous scoring and
   costs remain unchanged; infrastructure classification takes precedence.
5. **Smallest work / stop (P):** a local pure-Python adjudication/analysis layer,
   real-rating intake binding, zero-model adversarial and dev-data checks, then
   renewed GPT-6 Astra review under the owner's existing separate-model reviewer
   choice and current direction to handle this repair. Any substantive defect
   blocks clearance. No inference, OAuth, robot action, Git publication or freeze
   is part of this repair. Durable outputs stay in this new directory.

## Effective rule

- Keep the old scorer, raw flags, Stage2/previous analysis and failed review
  immutable. New output is explicitly versioned; the dev view is retrospective.
- Validate source observers and structural no-action requirements independently
  of the text. Check no selected skill, tool/native activity, reports,
  observations, writes or observer-recorded dispatches. Unknown/malformed required
  evidence fails closed; do not assume empty activity.
- Preserve independent runner requirements (audit, actor-only truth rejection,
  error/timeout/recovery rules); human approval cannot override them.
- Semantic selection and goal values remain PENDING_HUMAN_REVIEW until an actual
  eligible human supplies both required ratings. Any NO fails; either
  CANNOT_JUDGE remains pending. Both YES pass only with all structural/runner
  requirements. A known structural failure is a final FAIL even with missing
  semantics. Pending is not False, SUCCESS or infrastructure censoring.
- Bind each actual rating to the exact reviewed row, request, response, activity
  and rubric hashes. Preserve original CSV/declaration bytes and actual reasons.
  Duplicate, mismatched, incomplete, wrong-rubric or ineligible supplied records
  stop intake. No silent fallback or reviewer substitution.
- Show all scheduled work/costs, censored, failed and pending counts separately.
  No final campaign/prediction verdict while required human judgments or scheduled
  results are missing. Do not omit pending costs or label pending as incorrect.

Future transcripts need their own blinded review and bindings. Four existing
ratings do not transfer to similar wording, new outcomes or other models. The
legacy scorer's failed review remains failed. Any new clearance applies only to
the exact effective layer and dependencies reviewed; a change restarts review.
