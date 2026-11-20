# G1 three-model extension: pre-run decisions

Date: **2026-11-19**. Preparation authorized; benchmark launch requires a later owner acknowledgment of the combined preflight.
Every output is **exploratory backend, added after Sol and Qwen results**.

## Fixed scope and owner decisions

Run order and installed tags:
1. Ministral: ministral-3:8b-instruct-2512-q4_K_M.
2. Granite: granite3.3:8b.
3. Llama: llama3.1:8b-instruct-q4_K_M.

Reviewer: **Levinson**, nominated by the owner. Naming him is not a completed review or a verified eligibility declaration.
The owner explicitly chose: record an ineligible model as NOT RUN and continue with the next fixed model; do not substitute another.
Any other failed gate stops advancement. No benchmark launches during preparation.

Same 38 AI-authored cases, same condition/pair order, 76 attempts/model. No Qwen or Sol rerun, downloads, model-specific prompts, parser/template repairs, Gazebo, catalogue probe, first-turn replay, OAuth, Git commit/push/upload.
Protect the original 3,796 input hashes, scorer 90b0edd6d898ac749d121de29197a669593e022160503414413e0126766e8e4d, analysis, original Sol and Qwen artifacts.
All tests, controls, model checks and eventual trials run on the lab via SSH. Local document/artifact editing is allowed.

## Five-question research preflight

1. **Closest mechanism / change:** existing public bounded skill macros in rosa_reliability versus model-managed primitive execution with the same repaired ROSA interface. This is an additional-backend evaluation of existing code, not a new mechanism or novelty claim. Model identity and a separately recorded execution environment change; semantic policy does not.
2. **Observed need:** Qwen's 36 known-goal pairs yielded 26/36 primitive and30/36 macro passes;25 both-pass,5 macro-only,1 primitive-only,5 neither. Its eight write/partial-write cases yielded2/8 versus6/8;28 other cases24/28 each. All are retained observations. Earlier M4/integration findings were mixed, including Granite's text-formatted tool JSON and Llama's schema failures. These configurations may reproduce a floor rather than establish model capability.
3. **Decision / discriminator:** retain the fixed three-model sample irrespective of performance. Distinguish a replicated write-concentrated macro advantage from equal/reversed/undefined directions. Independent observer goal scoring remains separate from truthful skill reports, and ambiguous intent requires real human judgments.
4. **Fair reference:** both conditions receive identical information, model-specific digest, shared serving profile, tools, permissions, case text, feedback and bounds. The primitive arm remains capable of its frozen public operations; no scorer answers or privileged mappings are inserted. Condition wording remains confounded with execution mode. Unmodified ROSA is not a tested reference. No pooled accuracy or case-generalization claim.
5. **Smallest next step:** prepare three backend assemblies, eight scripted controls each, exact request serialization comparisons, metadata/full-GPU checks and an owner-readable combined preflight. Stop before benchmark launch. No new tasks or architecture are needed. After acknowledgment, at most228 attempts and1,833 charged model requests, independently capped611/model and8h/model. Expected inference count is approximately200/model from Sol200 and Qwen198, not a promise of runtime or an estimate for missing usage.

## Serving, accounting and recovery

Context8192, per-call output1024, per-task observed output2048, temperature0,seed42, reasoning=False,use_mmap=True,client cache=False. Preserve actual API stream=True and existing server prompt cache.
All three currently report tools, none reports thinking. Record thinking control as not applicable where absent; retain the common think=False request field without custom templates.
Per task:8 decision calls,360s,10 native operations,16 tool attempts,3 corrections,at most1 dispatch.
Per model:611 total charged requests, narrow HTTP502/503/504 retry reserve at most3. Empty-prompt load and unload requests are auxiliary model-endpoint requests and count toward611. Their missing internal token counters remain NOT_RECORDED.
Preflight may perform one empty-prompt load and one unload per tool-capable model, with no task generation. Those observed setup requests reduce remaining headroom. Setup/cleanup cannot evade the total cap. All POST generation requests are journaled before dispatch.
No benchmark output, completion prompt or behavioral compatibility probe is authorized in this preparation.
Preserve A3: recognized server/transport failures use pre-output/post-action censoring and never replay actions. Task deadlines, token/call budget stops, length stops, tool/schema errors and unidentified failures are not automatically infrastructure-censored. Only the frozen explicit HTTP rule permits a generation retry; local OOM/reset/restart/timeout failures do not gain retry rights.
Resume only unstarted cells after hash/audit/counter inspection, preserving the original per-model eight-hour origin. Never replace a failed, interrupted or censored attempt. No new stage or grant follows from recovery authorization.

## H-write: prospective for these added backends; post-hoc origin in Qwen

Write-bearing group: exactly8 frozen write and partial-write cases (four per domain); other known-goal group:28.
Compare **raw pass-count differences**, macro minus primitive, in the8-case group against the28-case group.
Status precedence, confirmed by owner before additional-model runs:
1. Uninformative if either write-bearing arm is at a floor0/8 or ceiling8/8; or censoring/pending judgments leave either compared group incomplete; or the model is ineligible/unrun.
2. Otherwise Support if macro has more write passes and its write-group difference exceeds its other-group difference.
3. Otherwise Against if primitive write passes are at least macro write passes.
4. Otherwise Uninformative.
Overall Support requires at least2 of the3 specified new models Support; Against requires at least2 Against; otherwise Uninformative. Ineligible or incomplete models do not lower that denominator.
These are descriptive statuses, not frozen P-predictions or confirmatory inference. Report counts, floors/ceilings, exclusions and per-model paired outcomes; do not pool passes across models.
The eight-case Qwen split is retrospective. An unpaired Fisher p-value around0.13 does not respect the actual paired/grouped design; paired discordance and uncertainty must be reported explicitly.

## Definition discrepancy and preserved gates

The request's T1 P-label correction is factually inconsistent with the adopted2026-11-14 amendment. That frozen amendment explicitly drops P3 (horizon reliability), assigns catalogue size to P4, and replaces the old depth contrast with P1-prime. Preserve the adopted identifiers. Record the discrepancy in a separate addendum rather than alter old reports or frozen sources.
Formal analysis cannot run through project_complete_rows while semantic judgments are pending. After execution, produce descriptive costs and a WITHHELD status; run the unchanged formal analyzer after actual ratings are bound. Do not reinterpret T4 as permission to bypass this gate.
The new pooled clarification kit is separate from Sol and Qwen Batch B. It contains at most12 new transcripts, shuffled with labels/mappings withheld and no generated ratings.

