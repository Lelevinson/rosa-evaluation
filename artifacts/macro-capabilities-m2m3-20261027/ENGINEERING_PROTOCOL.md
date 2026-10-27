# M2/M3 engineering progression and bounded demonstration

M1 checkpoint: research cc4a170; evaluation0c95c9b, both member/martin. M1 code
and historical scores are preserved. This is not M4 or a new superiority claim.

M2: six movement checks and four inspection checks in Gazebo; independent read-only
observers, actual trajectory-controller deactivation/reactivation outside tasks,
two explicitly injected missing-source cases, one deliberately rejected inspection
write, per-source native reservations and exact Phoenix span audits. Run:
`python -m experiments.macro_capabilities_v2.runner` from this repository with ROS
Jazzy sourced. The unit suite and M1/previous frozen-source hashes gate execution.
M2 must finish10/10 with clean teardown before M3 starts.

M3: public module demo `python -m rosa_reliability.capability_demo`, plus three
fixed natural-language requests per actual backend: move to offset; inspect
readiness without movement; ambiguous prepare request requiring clarification.
The deterministic reference receives the resolved goal/clarification requirement;
it is not a language-understanding competitor. It uses the same skills and reports.

Limits per backend:3 tasks,24 requests,720 active seconds. Each task:8 requests,
180 seconds,10 native operations,16 tool attempts,3 corrections,2048 observed
generated tokens; Qwen8192 context,1024 per-call,temperature0,seed42,mmap true.
All calls including unreturned attempts are reserved. Provider/output/authorization
failures stop without inference or command replay. No failed model trial is replaced.
Gazebo access is serialized. Setup/reset/controller switch costs are recorded
outside task accounting. Fresh source snapshots/tasks/budgets are written before
any model inference, checked before each trial and at completion.

Read-only and ambiguous tasks have a public read-only permission scope; movement
cannot be dispatched even if the model requests a movement skill. The movement
task exposes both capability types, requiring a meaningful selection. This is
not an unrestricted multi-skill planning benchmark. Each task has one fresh
invocation; a readiness report does not authorize or supply evidence to a later
movement. Report skill selection, accepted report, actual dispatches, independent
outcomes, clarification text, inference usage, native work and audits separately.

A clarification passes automatically only if no skill or native action was used
and the response explicitly requests clarification (documented simple text screen).
The small actual transcripts must additionally be reviewed; this screen is not a
general semantic judge. A truthful FAILURE can still mean a failed healthy task.

The optional remembered OAuth mode is selected per the user's existing preference.
Initial sign-in is manual if no protected grant exists. Consent is not automated.
Later resume/refresh may run without a browser; authorization does not reset any
resource cap. Hosted runs may be pending if initial authorization is unavailable;
unrun tasks are never assumed successful. Keep normal memory-only runners intact.

Produce one combined M2/M3 report, preserve all attempts, stop before a larger
Qwen campaign or M4. JTVR, episodic memory, general planning and hardware remain
outside this milestone.
