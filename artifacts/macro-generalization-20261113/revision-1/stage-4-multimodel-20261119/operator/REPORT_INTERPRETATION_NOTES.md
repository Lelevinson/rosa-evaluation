## Integration and environment

Granite produced76 text responses and zero recognized native calls; no native
operations executed. An inspected response rendered tool-shaped JSON in a code
fence and prose. One primitive response hit its output limit. Tool-capability
metadata and full GPU loading did not demonstrate functional tool calling. These
results characterize a failed tested integration, not intrinsic task incapacity.

Llama produced383 recognized native calls, but schema/argument adherence and
recovery failed repeatedly:150/135 invalid attempts and37/31 budget endings P/M.
An inspected read call used incompatible node/fields arguments. One macro
known-goal task passed; the remaining known-goal tasks failed. Native-call parsing
and successful end-to-end task execution are different requirements.

Ministral is the strongest of the three new local configurations on these cases:
known-goal correctness28/36 →33/36, with six macro-only and one primitive-only
correct pair. The point difference is exploratory; small, grouped cases do not
establish a general reliability advantage. Its primitive40 versus macro5 invalid
attempts and native102 versus127 operations should accompany the call savings.

Every sampled loaded-model observation was fully GPU-resident at8K context:
Ministral96/96, Granite89/89, Llama80/80. Sampling observed the Ollama runner and
the existing GNOME remote-desktop compute process. Samples do not prove continuous
absence of competing work. Raw utilization, clocks, temperatures and residency are
retained; no causal thermal or hardware comparison is inferred.

Common serving: context8192, maximum1024 output/call, observed task-output gate2048,
temperature0, seed42, use_mmap true, client cache false, think=false and actual API
streaming true. The server cache stayed as-is. None of these three advertised
thinking capability. Per task:8 decisions,360s,10 native operations,16 tool attempts,
3 corrections and at most1 dispatch. Each backend kept its own611-request cap and
eight-hour clock. Models ran sequentially on the lab via SSH.

The extension image is
`sha256:306205ffce29f89a7e138f130cd3ee0bd668c17ed5441a45532449dbcbf771d2`,
different from Qwen's earlier image. Pinned dependencies matched and all24 scripted
preparation controls passed. Driver570.195.03 and reported CUDA compatibility12.8
are recorded; compatibility is not an installed-toolkit assertion. These are mock
arm/base operations inside a ROS2 Jazzy/ROSA environment, not new Gazebo,
controller or physical-robot tests.

## Preserved errors and corrections

1. Three metadata values were transcribed incorrectly into the acknowledged
   preflight prose: Ministral disk bytes and digest, and Llama loaded size. Actual
   sealed configurations and live digest checks were correct and unchanged. The
   original acknowledged record remains intact. The dated preflight correction
   supplies exact authoritative values.
2. The automatic report worker initially invoked a host Docker verifier inside
   the container, where the Docker CLI was absent. It stopped after all trials
   completed. A reporting-only continuation ran the stdlib consolidator on the
   host. No trials or inference were repeated. Failed source, status and logs are
   retained.
3. The first descriptive helper used nonexistent kind `partial_write`, omitting
   the two actual `write_fault` cases and displaying6/30. The corrected helper uses
   frozen kinds `write` and `write_fault`, asserting8/28 per arm. Original source,
   derived outputs and the completed raw archive remain unchanged. **Use
   DESCRIPTIVE_EXTENSION_RESULTS_CORRECTED01.json and this report for subgroup
   counts.** Scorer, frozen analyzer, hypotheses, thresholds and raw results did
   not change.

The original3,796 frozen inputs,1,159 retained Sol/Qwen hashes and three backend
seals reverified. All228 raw trial hashes and2,019 entries of the initial completed
archive verified locally. Its derived subgroup table is superseded, so the share
package supplies the corrected report/JSON separately and marks them authoritative.
This package is not a live Phoenix database backup. Original runtime prerequisites
and model weights retain their separately recorded hashes/provenance; no model
weights are uploaded or newly downloaded.

## Claims, limitations and next action

These results support reduced LLM orchestration overhead for Ministral in this
environment, with a favorable known-goal point difference. They do not establish
a new selection algorithm, broad reliability improvement, superiority to stock
ROSA, parity with Sol, or a replacement for original Qwen/M4 results. Equal token
limits do not mean equal semantic output across tokenizers. Granite/Llama failure
times cannot support useful-task efficiency claims.

All cases are AI-authored and reused across models; backends were added after
Sol/Qwen results were seen. Condition wording remains confounded with execution
mode, the catalogue is bounded, and samples are small and grouped. Interpretation
must preserve model/integration/environment differences and all failures. There
was no per-model prompt, schema, parser or template repair.

Send only the neutral12-transcript extension review ZIP to Levinson. Obtain his
actual CSV and honest eligibility declaration. Keep Qwen's four-transcript Batch B
separate. Then bind ratings and run the unchanged frozen analyzer separately for
each backend with its original endpoint scopes. T6 remains BLOCKED until then;
no final human-adjudicated campaign verdict or H-write closeout is claimed. P3 is
dropped horizon reliability; P4's catalogue probe was not run; P1′ remains formally
Sol-specific. No further model run, architecture change or Git publication starts
from this report.
