# Public-API compatibility stop and required design decision

Date: **2026-11-13**. Status: **STOPPED_INTERFACE_INCOMPATIBLE**.

The mobile-base domain is not inherently incompatible with the module. A
single-node numeric x/y/yaw target and a fixed Boolean inspection can be supplied
through existing transport interfaces. The incompatibility is with **the exact
multi-source acquisition design requested for G1**.

## What the current code actually provides

1. `StateSkill` is a frozen strict schema containing skill_id and targets. It
   requires exactly one canonical target node; there is no prerequisite-source
   or guard declaration. `_RegisteredSession.write` checks a known observation
   of that same target node. It does not require three separately recorded inputs.
2. `MacroSession.run_workflow` is a fixed target read, optional target write,
   and fresh verification. On a healthy initially off-target task this is three
   native operations, not a configurable p+2 path. Adding three Boolean values to
   one pose response would neither create three metered sources nor their policy.
3. `InspectionSkill` can declare multiple source groups. Each read/verify loops
   through all selected groups, reserving one native operation per group. Thus
   native depth1/2/4/6 is feasible. However, the public read request accepts only
   the selected subject; it cannot choose one source/subset. The primitive-style
   path has select/read/report, three model calls at every depth. A transport
   cannot expose selective reads that the tool schema never requests.
4. The capability catalogue exposes state targets and inspection checks, but
   not state prerequisite contracts. The two write anchors cannot fairly differ
   by p=1 versus p=3 under that unchanged contract.

`source-compatibility.json` provides exact source files, method line numbers and
digests. This is static source/API inspection. No scripted reference-path controls,
model trials, local trace audits or Phoenix audits were run.

## Required diff if the study is retained exactly

This is a description of a possible **new version**, not an applied patch:

- Extend the public state-skill contract with typed prerequisite source/field
  requirements and safe/unsafe/unknown semantics, separate from target pose.
  Expose them to both arms under a common catalogue schema. This changes the
  M4 catalogue schema; it cannot be presented as unchanged-schema reuse.
- Extend public primitive acquisition to request an allowed source subset with
  per-source metering. Ensure the primitive arm can batch all independent reads.
  Do not require serial calls merely to make macros look better.
- Extend the bounded macro to acquire the declared prerequisites, block unknown
  or unsafe writes, conditionally dispatch once, and verify the outcome freshly.
  Extend freshness/provenance validation so preread evidence cannot masquerade
  as goal verification. Keep independent observer truth outside the agent.
- Validate limits, task-local reports, partial acquisition, unknown evidence and
  exactly-once dispatch in a separate engineering milestone. Only then propose
  a new frozen G1 protocol. No present experiment can supply those validations.

Affected implementation areas would include `bounded_macro.py` (public schema
and invocation), `capabilities.py` (catalogue/source selection/acquisition), and
`macro.py` or a new explicitly versioned bundle policy (prerequisite sequencing).
Tool argument schemas and freshness/report validation in `reference.py` and its
underlying execution/evidence layer would need review. Exact patch size and the
complete necessary file set are **not recorded**; no patch was written or tested.
It would be misleading to call this a one-line transport-only adaptation.

## Other design contradictions to resolve before spending model calls

- M4's full query hard-codes eight calls, ten operations, sixteen attempts and
  joint tolerance in radians. G1 requests per-skill variable budgets and a mobile
  domain. The exact system/RULES/condition sentences are saved, but a parameterized
  budget/unit suffix needs an explicit interpretation/approval. No silent rewording.
- Existing `experiments.reliability_v2.cases.MockTransport` is a usable candidate
  arm-state engine, with separate actor records and injected faults. Its old
  runner obtains mock truth by copying that same object's values. That is not
  the requested independent observer with its own state, transport and records.
  Therefore this preparation cannot confirm the requested observer already exists.
- A future mock server could reuse the state-update engine behind distinct actor
  and read-only observer channels. Observer snapshots/records must not alias the
  actor cache; both observe one authoritative simulated world, not two unrelated
  worlds. That harness is permitted in this directory but is not implemented.
- All proposed prerequisite reads are independent of one another. There are
  read-to-write and write-to-verification dependencies, but **no dependent-read
  acquisition cases**. A dependent-read subgroup would be absent, not inferred.
- For ambiguous requests there is no unique target skill. The target-plus-two
  distractor rule needs a separately predefined catalogue sampler for those cases.
- The Stage5 selection probe needs a choice between one fixed condition sentence
  and a crossed two-sentence factor. The latter doubles its request ceiling.
- The supplied0.8 gives no actual P1-P4 statements or numeric thresholds, despite
  referring to defaults. The prediction file contains newly proposed defaults,
  explicitly unconfirmed. They must not be attributed to the supplied prompt.

## Recommendation

Do not implement a new acquisition planner or silently alter the public module
for this deadline-driven study. Prefer a revised, narrower G1 using actual
independent-source batching and the existing three-operation write macro. That
can test second-domain reuse, catalogue-size sensitivity and observed batching
costs. Its native-depth ladder may legitimately yield **no increasing model-call
benefit**; report that outcome rather than forcing serial primitive calls.

Alternatively authorize a separately versioned engineering extension first,
accepting the added scope and changed schema. Either option changes the present
design and requires a new confirmed note before Stage1. This package does not
select or execute either option.

P5 is **Against** for the narrow proposition “the exact requested G1 catalogue
and acquisition policy can be hosted through the current public API unchanged.”
It is **Uninformative** about live two-domain performance, since no domain control
or model experiment was run. No general claim that mobile bases cannot use ROSA
is supported.
