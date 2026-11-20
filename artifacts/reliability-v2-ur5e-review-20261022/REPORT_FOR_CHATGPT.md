# Reliability v2: complete experiment and UR5e transfer report

This prospective study preserves every earlier campaign. It is a bounded exploratory comparison, not a powered confirmatory study or robot safety certification.

Independent audit: **PASS**. Live trials: 96; model calls: 482.
OAuth cleanup: REVOKED; actual refreshes: 0.

The original automatic campaign completed80 validation/mock trials, then stopped at an independently failed UR5e home reset before any model-driven arm trial. Its failure, failed gate, revoked session and power release remain preserved. A separately frozen ur5e-transfer-v1 follow-up adds an outside-trial check that both controllers are active; all four deterministic controls passed before its16 model trials. This collection completes the work across those two versions, not a claim that the first attempt completed uninterrupted.

Background erratum: earlier progress messages and the follow-up protocol incorrectly described Qwen as32/32 correct in the main mock matrix. It completed32 trials but passed28: A6/8,B8/8,C8/8,D6/8. Sol passed32/32. BACKGROUND_CORRECTION.md preserves this correction without editing the frozen protocol. All original scores remain unchanged.

## Results

|Backend|Phase/arm|Correct|Achievable verified|Fault handling|Invalid attempts|Unsupported success|Calls|Native ops|Seconds|Trace audits|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|ollama|gazebo/A|1/4|0/1|1|1|0|11|5|234.802|4/4|
|ollama|gazebo/D|1/4|0/1|1|1|0|11|5|218.374|4/4|
|ollama|mock/A|6/8|4/5|2|6|0|46|32|544.055|8/8|
|ollama|mock/B|8/8|5/5|3|3|0|46|32|553.443|8/8|
|ollama|mock/C|8/8|5/5|3|3|0|42|34|552.567|8/8|
|ollama|mock/D|6/8|4/5|2|6|0|44|35|553.004|8/8|
|ollama|validation/A|4/4|2/2|2|1|0|22|15|270.899|4/4|
|ollama|validation/D|4/4|2/2|2|1|0|20|15|253.500|4/4|
|siwc|gazebo/A|4/4|1/1|3|0|0|20|12|95.204|4/4|
|siwc|gazebo/D|4/4|1/1|3|0|0|19|14|91.947|4/4|
|siwc|mock/A|8/8|5/5|3|1|0|41|28|125.095|8/8|
|siwc|mock/B|8/8|5/5|3|1|0|42|30|126.833|8/8|
|siwc|mock/C|8/8|5/5|3|1|0|41|35|125.613|8/8|
|siwc|mock/D|8/8|5/5|3|1|0|40|33|125.022|8/8|
|siwc|validation/A|4/4|2/2|2|0|0|18|12|52.955|4/4|
|siwc|validation/D|4/4|2/2|2|0|0|19|15|57.509|4/4|

## Prospective decision

- siwc/mock: D minus A correct=+0; calls=-1; native operations=+5; wall ratio=0.999; retention screen=False.
- siwc/gazebo: D minus A correct=+0; calls=-1; native operations=+2; wall ratio=0.966; retention screen=False.
- ollama/mock: D minus A correct=+0; calls=-2; native operations=+3; wall ratio=1.016; retention screen=False.
- ollama/gazebo: D minus A correct=+0; calls=+0; native operations=+0; wall ratio=0.930; retention screen=False.

## Paired mechanism comparisons

|Backend|Comparison|Left only correct|Right only correct|Both correct|Both incorrect|Call difference|
|---|---|---:|---:|---:|---:|---:|
|siwc|B vs A|0|0|8|0|+1|
|siwc|C vs A|0|0|8|0|+0|
|siwc|D vs A|0|0|8|0|-1|
|siwc|D vs B|0|0|8|0|-2|
|siwc|D vs C|0|0|8|0|-1|
|ollama|B vs A|2|0|6|0|+0|
|ollama|C vs A|2|0|6|0|-4|
|ollama|D vs A|0|0|6|2|-2|
|ollama|D vs B|0|2|6|0|-2|
|ollama|D vs C|0|2|6|0|+2|

## Matched deterministic UR5e controls

|Case|Outcome|Expected|Independently consistent|Skill operations|Model calls|Seconds|
|---|---|---|---|---:|---:|---:|
|ur5e_coordinated_move|SUCCESS|SUCCESS|True|3|0|4.017|
|ur5e_suppressed_command|FAILURE|FAILURE|True|3|0|4.019|
|ur5e_partial_trajectory|FAILURE|FAILURE|True|3|0|4.019|
|ur5e_missing_sensor|UNKNOWN|UNKNOWN|True|1|0|0.008|

When the retention screen is not met, prefer A and document the negative or inconclusive result. Do not call a guard-assisted corrected task error-free model behavior.

## What was compared and what was not

A/B/C/D all use actual ROSA with the same repaired node-keyed interface, safety/report gates and equivalent retry/operation/model budgets. A is a competent shared-platform reference, not untouched upstream ROSA. B changes only the representation of identical error facts; C adds immediate framework verification; D combines them. No report values or identifiers are automatically repaired. Fresh trusted reads are reusable in all arms, avoiding the old named-verifier artifact.

Fresh validation preceded the main mock matrix. Both model phases and exact persisted Phoenix audits preceded installation and deterministic testing of the UR5e. Deterministic controls preceded any model-driven six-axis trials. All failures and interrupted attempts remain data; no live tuning or selective reruns are permitted.

The main matrix has eight case pairs per arm/backend: five achievable cases and three fault cases. Automatic checks can add work without improving outcomes. These small denominators and one local/one hosted backend do not establish generalization or a special benefit for all small models. Wilson intervals in the JSON are descriptive and do not account for heterogeneous paired cases. No statistical significance claim is made.

The Invalid attempts column counts all validation/prerequisite rejections. In the transient-controller case, the first busy rejection is an injected environmental condition, not an intrinsically malformed or unsafe model decision. The JSON rejection_attribution separates these expected transient rejections from schema errors, blocked UNKNOWN-state writes and other contract/semantic rejections. A final pass after a guard rejection credits the combined system; it does not erase the original attempted call.

A concrete interface limitation remains in the tested implementation: write_state retains the top-level goal_verified=false receipt field even when its nested automatic verification contains goal_reached=true. The nested observation is valid and the report gate uses it, but this mixed signal may encourage redundant manual checks. The common prompt also asks for fresh read/verification evidence without explicitly instructing the model to skip a manual check when automatic evidence is already returned. These are possible explanations, not established causal diagnoses. The frozen campaign was not edited after observing behavior. Do not interpret its overhead as proof that automatic verification in general is ineffective; a future correction needs a new prospective validation.

The apparent Qwen mock advantage of B/C over A/D is not proof of a causal mechanism. The two A/D failure families are missing-one-node and first-read-timeout. Automatic verification cannot affect a decision made before any write; likewise B/D share the structured-feedback path before a write. Visible acquisition timestamps, case order and nondeterministic backend behavior can change generated decisions even with a fixed seed. One trial per case/arm is insufficient to distinguish these effects. Treat B/C as follow-up candidates, not demonstrated general improvements.

Full-arm transfer uses a vendor UR5e model, standard ROS2 trajectory controller, three-second bounded joint-space trajectories and independent JointState observations. Command suppression, partial trajectory and sensor unavailability are deliberate injections. An empty-world position-controlled trajectory is more realistic than the old one-joint fixture, but does not test grasping, perception, obstacles, collision planning, hardware or physical safety.

The independent observer is separate from agent claims/cache but uses the same trusted simulator and sensor source. It is not an independent physical sensing technology. Task goals are explicitly supplied as joint/value dictionaries; a deterministic controller is expected to be sufficient for these typed goals.

## Raw outcomes and failures

- ollama/validation/004-validation_missing-D: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/validation/005-validation_missing-A: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- siwc/mock/028-transient_write_prerequisite-B: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- siwc/mock/029-transient_write_prerequisite-C: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- siwc/mock/030-transient_write_prerequisite-D: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- siwc/mock/031-transient_write_prerequisite-A: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/004-missing_one_node-D: correct=False, invalid=4, unsupported SUCCESS=0, API/limit failure=True. See that trial's raw evidence and model messages.
- ollama/mock/005-missing_one_node-A: correct=False, invalid=4, unsupported SUCCESS=0, API/limit failure=True. See that trial's raw evidence and model messages.
- ollama/mock/006-missing_one_node-B: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/007-missing_one_node-C: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/008-first_read_timeout-D: correct=False, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/009-first_read_timeout-A: correct=False, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/010-first_read_timeout-B: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/011-first_read_timeout-C: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/028-transient_write_prerequisite-B: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/029-transient_write_prerequisite-C: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/030-transient_write_prerequisite-D: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/mock/031-transient_write_prerequisite-A: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/gazebo/000-ur5e_coordinated_move-A: correct=False, invalid=0, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/gazebo/001-ur5e_coordinated_move-D: correct=False, invalid=0, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/gazebo/002-ur5e_suppressed_command-D: correct=False, invalid=0, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/gazebo/003-ur5e_suppressed_command-A: correct=False, invalid=0, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/gazebo/004-ur5e_partial_trajectory-A: correct=False, invalid=0, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/gazebo/005-ur5e_partial_trajectory-D: correct=False, invalid=0, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/gazebo/006-ur5e_missing_sensor-D: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.
- ollama/gazebo/007-ur5e_missing_sensor-A: correct=True, invalid=1, unsupported SUCCESS=0, API/limit failure=False. See that trial's raw evidence and model messages.

## Rejection attribution

- ollama/validation/004-validation_missing-D: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=True.
- ollama/validation/005-validation_missing-A: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=True.
- siwc/mock/028-transient_write_prerequisite-B: expected_transient_controller_rejection; write_prerequisite_rejected; details={"reason": "temporary controller busy; retry this prerequisite once within the same budget"}; final combined pass=True.
- siwc/mock/029-transient_write_prerequisite-C: expected_transient_controller_rejection; write_prerequisite_rejected; details={"reason": "temporary controller busy; retry this prerequisite once within the same budget"}; final combined pass=True.
- siwc/mock/030-transient_write_prerequisite-D: expected_transient_controller_rejection; write_prerequisite_rejected; details={"reason": "temporary controller busy; retry this prerequisite once within the same budget"}; final combined pass=True.
- siwc/mock/031-transient_write_prerequisite-A: expected_transient_controller_rejection; write_prerequisite_rejected; details={"reason": "temporary controller busy; retry this prerequisite once within the same budget"}; final combined pass=True.
- ollama/mock/004-missing_one_node-D: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=False.
- ollama/mock/004-missing_one_node-D: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=False.
- ollama/mock/004-missing_one_node-D: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=False.
- ollama/mock/004-missing_one_node-D: contract_or_semantic_rejection; outcome_classification_mismatch; details={"observed_outcome": "UNKNOWN"}; final combined pass=False.
- ollama/mock/005-missing_one_node-A: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=False.
- ollama/mock/005-missing_one_node-A: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=False.
- ollama/mock/005-missing_one_node-A: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=False.
- ollama/mock/005-missing_one_node-A: contract_or_semantic_rejection; outcome_classification_mismatch; details={"observed_outcome": "UNKNOWN"}; final combined pass=False.
- ollama/mock/006-missing_one_node-B: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=True.
- ollama/mock/007-missing_one_node-C: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=True.
- ollama/mock/008-first_read_timeout-D: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=False.
- ollama/mock/009-first_read_timeout-A: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=False.
- ollama/mock/010-first_read_timeout-B: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=True.
- ollama/mock/011-first_read_timeout-C: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=True.
- ollama/mock/028-transient_write_prerequisite-B: expected_transient_controller_rejection; write_prerequisite_rejected; details={"reason": "temporary controller busy; retry this prerequisite once within the same budget"}; final combined pass=True.
- ollama/mock/029-transient_write_prerequisite-C: expected_transient_controller_rejection; write_prerequisite_rejected; details={"reason": "temporary controller busy; retry this prerequisite once within the same budget"}; final combined pass=True.
- ollama/mock/030-transient_write_prerequisite-D: expected_transient_controller_rejection; write_prerequisite_rejected; details={"reason": "temporary controller busy; retry this prerequisite once within the same budget"}; final combined pass=True.
- ollama/mock/031-transient_write_prerequisite-A: expected_transient_controller_rejection; write_prerequisite_rejected; details={"reason": "temporary controller busy; retry this prerequisite once within the same budget"}; final combined pass=True.
- ollama/gazebo/006-ur5e_missing_sensor-D: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=True.
- ollama/gazebo/007-ur5e_missing_sensor-A: blocked_unknown_state_write; write_prerequisite_rejected; details={"reason": "read current state first; unavailable observations cannot authorize a write"}; final combined pass=True.

## Generation-length termination

The local profile fixes num_predict=256. The following rows have actual provider metadata done_reason/finish_reason=length, counted once per LLM span rather than once per duplicated serialized metadata object. Incomplete prose treated as an agent final response is an end-of-turn/continuation limitation under this tested profile. It does not establish that Qwen cannot control the arm with a different output budget or a bounded continuation policy. Neither was changed during this experiment.

- ollama/gazebo/000-ur5e_coordinated_move-A: 1 length-terminated generations; final combined pass=False.
- ollama/gazebo/001-ur5e_coordinated_move-D: 1 length-terminated generations; final combined pass=False.
- ollama/gazebo/002-ur5e_suppressed_command-D: 1 length-terminated generations; final combined pass=False.
- ollama/gazebo/003-ur5e_suppressed_command-A: 1 length-terminated generations; final combined pass=False.
- ollama/gazebo/004-ur5e_partial_trajectory-A: 1 length-terminated generations; final combined pass=False.
- ollama/gazebo/005-ur5e_partial_trajectory-D: 1 length-terminated generations; final combined pass=False.

## Evidence and reproducibility

freeze.json contains exact source digests and source/ contains byte-for-byte snapshots. schedule.json fixes validation and mock order; frozen arm.py fixes arm cases. Each trial includes result.json, raw evidence.json, local trace.json and independently retrieved phoenix-trace.json. Phase audit JSONs compare exact span-ID sets. independent-review.json replays mock state transitions and call-time claims rather than grading against a later final state.

Package versions, serving profiles, model runtime metadata, controller package versions, simulator logs, independent reset observations, command records, temporary power hold/release and resource samples are retained. Initial cold loading and host scheduling can affect latency; treat timing as descriptive rather than a causal speedup proof. Model calls and native work are the more interpretable cost counts.

Previous Baseline v1, Stage4 and reliability v1 records and archives are not rescored or rewritten. Full JTVR remains paused; episodic memory remains optional.

## Recommended next steps

Choose the simplest configuration supported by measured benefit. Review every invalid/unsupported attempt before expanding scope. If outcomes tie, do not add more copies of the same easy templates: identify a distinct naturally occurring failure mode and preregister a focused intervention study. Keep real ROS2 skill/controller boundaries and independent physical outcome checks. Extend to a constrained task with an explicit reason to use language reasoning only after this evidence is reviewed.

The concrete next engineering candidates are: (1) remove the contradictory verification-status field for every model, with a new prospective contract; (2) detect provider length termination and test a bounded continuation/completion policy that never executes partial tool arguments, never repeats an uncertain robot command, and charges all retries to the original request/native/time budgets; (3) keep raw timestamps and sensor precision in evidence logs while evaluating a stable, documented model-facing representation. Compare continuation against concise-instruction-only and explicitly budgeted output-limit baselines rather than crediting extra compute or a weakened reference. These are recommendations, not changes silently applied to this campaign.

## Audit errors

[]
