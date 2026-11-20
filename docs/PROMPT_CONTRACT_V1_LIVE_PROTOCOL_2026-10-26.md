# Focused live validation of the common prompt repair

Prospective engineering validation, not a held-out efficacy study. Freeze all
listed sources and this protocol before any live inference. Preserve all prior
source/evidence packages and their original scores.

## Question and treatment

Can actual Qwen and Sol execute the five-tool bounded contract without the
generic ROSA discovery-tool contradiction? The only agent change relative to
the preceding macro campaign is the opt-in common prompt-prefix replacement.
Robot-specific instructions, user queries, skills, schemas, controller,
permissions, accepted-report handling, truncation handling, scoring and per-trial
budgets stay unchanged. Both models and all three conditions receive the same
common system contract. Macro and workflow receive identical task wording.

## Schedule

Three KNOWN development cases: already_home (avoid unnecessary motion),
missing_prerequisite (UNKNOWN and no motion), transient_after_motion (one motion,
observe injected failure, then bounded read-only recovery). Each uses the
model-managed primitive, straightforward macro and program-managed workflow
conditions. Nine trials per backend, eighteen total, one run per cell.
The existing counterbalanced schedule is filtered without adaptive reordering.
Six independent deterministic controls run before each backend. Gazebo access
is serialized; each task resets to home. Only simulation is authorized.

## Resources and authentication

Each backend: at most72 inference requests and4500 active seconds. Each trial:
8 model calls,180 seconds,16 tool attempts including nested steps,10 native
operations,3 invalid corrections and one dispatched write. Qwen remains
qwen3.5:9b Q4_K_M (digest56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90),
Ollama0.40.6, context8192, output<=1024/call, temperature0, seed42,
reasoning/streaming/cache off. Generated-output threshold2048/trial stays
unchanged; hosted overshoot is observed/accounted before tool dispatch rather
than represented as a guaranteed provider-side cap. Sol is gpt-6.1-sol using
the existing ChatSiwc adapter, with manual initial consent, validated scopes,
memory-only renewal and normal revocation. No credential persistence/migration.
Unavailable authorization/quota saves progress and stops; no automatic rerun
or replay. Unknown costs of unreturned requests remain censored, not zero.

## Evidence and gates

Record actual model inputs and verify their common prefix and original user
goal on every inference. Preserve usage, responses, all actors, independent
state/claim-time oracles, faults actually exercised, local spans and exact
server-side Phoenix span matches. Write results/checkpoint before auditing.

Engineering gate: all planned trials complete, actual-input checks pass,
six controls/backend pass, all local and persisted trace audits pass, no hard
budget violation, unsupported accepted success or unauthorized/replayed write;
normal simulator and OAuth cleanup verified. Task failures remain model/system
results and are not silently reclassified as instrumentation failures.

Progression additionally requires every known case/condition to meet its frozen
outcome-and-fault-coverage contract for both backends. If this strict development
readiness screen fails, report the failures and review scope before a new live
pilot. Do not tune the prompt during the batch or rerun failures until passing.
Any later amendment/new study receives a separate version and source freeze.

No causal prompt-effect estimate is claimed from historical comparisons:
this is a small, nonrandomized known-case validation. A later fresh study needs
its own frozen cases, repetitions, meaningful benefit criteria and budgets.
