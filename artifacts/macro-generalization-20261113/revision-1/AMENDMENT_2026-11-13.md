# G1 revision 1 — dated Stage 0 amendment

Date: **2026-11-13**. Scope: new preparation only; no live experiment.

This revision preserves the [original stopped report](../README.md),
[STOPPED_INTERFACE_INCOMPATIBLE checkpoint](../STAGE0_CHECKPOINT.json),
[original pre-run note](../PRE_RUN_NOTE.md), and all original cases, code and
manifests unchanged. Outputs for this revision stay under revision-1.

The original p3 acquisition design was not supported by the existing public
API. G1 now uses four all-source inspection bundles and one ordinary single-node
state-change skill per domain:5/domain,10 combined. Inspection native depth
remains1/2/4/6, with expected primitive3 versus macro2 model turns. Movement
nominally has3 native operations and expected primitive5 versus macro2 turns.
These are expected paths pending Stage1, not measured model results.

The central hypothesis changes from increasing native acquisition depth yielding
larger bundling benefit to **removing model decision turns while native work stays
explicitly metered**. The old predictions are not overwritten or reclassified.
No performance experiment has tested either version. p3 prerequisites, selective
source acquisition and horizon-dependent reliability are deferred to **G2**.

New mock worlds and separate observer transports are implemented entirely here.
No old mock oracle is reused. Arm targets use radians; the base uses metres and
fractions, with localization/map-lease/battery/path semantics and distinct faults.
The observer sees the same authoritative world through a different read-only
interface; it never reads the actor's cache. Independence means separate state,
transport and records, not independent authorship or sensing technology.

The revised case target is16 dev and38 held-out-designated. The owner requested
AI-authored drafts; their authors are recorded accurately. There are **zero real
teammate-authored cases**. The original independent-authorship criterion is not
satisfied, and must not be reported as passed. No G1 control/model stage is
authorized by the case drafts. Advancing with an AI-only case set would require
the confirmation to explicitly adopt that methodological change.

All M4 task limits and original Qwen A settings are retained. The system prompt,
RULES and both condition sentences are unchanged. Only domain B replaces the
joint-tolerance sentence with the recorded metres/fraction sentence, identically
for both arms. No plain-language catalogue descriptions or prompt tuning are added.
The execution-mode/condition-wording confound remains.

Stage0 includes observer-separation unit tests and public-API construction/schema
checks, as requested. It does **not** include Stage1 fake-model reference paths,
live model turns, local full-trial trace audits or persisted Phoenix matching.
Those remain gated on user confirmation. The preparation manifest is a proposal
checkpoint, not the final post-dev experiment freeze.
