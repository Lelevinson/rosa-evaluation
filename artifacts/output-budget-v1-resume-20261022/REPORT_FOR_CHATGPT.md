# Qwen output/interaction diagnostic v1 â€” complete report

Fresh Qwen-only UR5e diagnostic. Historical96-trial study is preserved. No OAuth requests.
The original first R256 trial reached the robot goal but timed out before reporting; it remains FAILED with its original completed_usage_records audit exception. A separately frozen timeout-accounting follow-up saved34 additional results before its supervisor ended and WSL was found stopped during entry035 (healthy L512 repetition1). The35 completed scores and original RUNNING interruption checkpoint remain unchanged. Fifteen persisted partial spans were recovered, but no independent final score exists for that interrupted attempt.
A separately frozen restart repeated four deterministic controls and ran only the five unfinished entries. Entry035 is an explicitly labeled replacement; four others had not started. This collection contains41 attempts:40 scored completions and1 UNKNOWN/unscorable external interruption. Rates below are descriptive complete-case rates; L512 had9 attempts,8 scored and1 unscorable. No completed trial was rerun or rescored. All40 scored-trial persisted span-ID sets/closed trees are independently checked; the unfinished partial trace is archived separately and is not declared complete. Known usage for an interrupted generation is a lower bound. Cost tables cover scored trials only; additionally reserve up to8 calls and2048 output tokens for the unscorable attempt. Original320-call/81920-output/3-active-hour ceilings remain satisfied. Restart/cold-loading/order and unknown interrupted usage limit comparisons.
Independent audit: **PASS**; completed trials: 40/40.

## Configuration and interpretation

L256/L512/L1024 vary per-response output allowance only. C256 adds concise tool-first instructions. R256 enables bounded pre-parser length recovery. Every condition uses repaired A, context8192, the same model/quantization/seed,2048 total generated tokens,8 calls,180seconds,10 native operations and at most1 dispatched write. Two repetitions/case; exploratory, not confirmatory. All40 were frozen together with block ordering before live inference.

Recovery does not repair argument values or replay commands. It discards calls in a length-stopped response and requests a fresh next step within the original budgets. Any improvement is credited to the combined system. The disabled reference retains the original end handling. No automatic-verification changes were mixed into this study.

## Results

|Condition|Correct /8|Healthy /2|Fault /6|Calls|Known output tokens|Output upper bound|Unknown-usage trials|Recorded length stops|Recoveries|Invalid|Unsupported SUCCESS|Seconds|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|L256|2|0|2|24|3466|3466|0|6|0|3|0|474.6|
|L512|3|0|3|42|7589|8101|1|3|0|7|0|1095.7|
|L1024|5|1|4|48|8425|10473|2|0|0|9|0|1255.0|
|C256|1|0|1|25|3520|3520|0|6|0|5|0|497.9|
|R256|2|0|2|49|7791|8303|2|16|12|6|0|1083.8|

## Conclusions from this diagnostic

- L512: correct outcomes versus reference +1; healthy 0/2; paired regressions 1; known output-token difference +4123 (not exact if usage is incomplete); calls +18; prospective candidate screen=False. This small diagnostic does not establish a general improvement.
- L1024: correct outcomes versus reference +3; healthy 1/2; paired regressions 1; known output-token difference +4959 (not exact if usage is incomplete); calls +24; prospective candidate screen=False. This small diagnostic does not establish a general improvement.
- C256: correct outcomes versus reference -1; healthy 0/2; paired regressions 1; known output-token difference +54 (not exact if usage is incomplete); calls +1; prospective candidate screen=False. This small diagnostic does not establish a general improvement.
- R256: correct outcomes versus reference +0; healthy 0/2; paired regressions 0; known output-token difference +4325 (not exact if usage is incomplete); calls +25; prospective candidate screen=False. This small diagnostic does not establish a general improvement.

## Paired differences versus fresh L256

[
  {
    "condition": "L512",
    "candidate_only_correct": 2,
    "reference_only_correct": 1,
    "both_correct": 1,
    "both_incorrect": 4
  },
  {
    "condition": "L1024",
    "candidate_only_correct": 4,
    "reference_only_correct": 1,
    "both_correct": 1,
    "both_incorrect": 2
  },
  {
    "condition": "C256",
    "candidate_only_correct": 0,
    "reference_only_correct": 1,
    "both_correct": 1,
    "both_incorrect": 6
  },
  {
    "condition": "R256",
    "candidate_only_correct": 0,
    "reference_only_correct": 0,
    "both_correct": 2,
    "both_incorrect": 6
  }
]

## Every trial

|Trial|Correct|Observed goal|Accepted report|Calls|Output tokens|Length stops|Recoveries|Seconds|
|---|---|---|---|---:|---:|---:|---:|---:|
|000-r0-ur5e_coordinated_move-R256|False|True|None|7|1026|2|2|180.4|
|001-r0-ur5e_coordinated_move-L1024|False|True|None|6|911|0|0|180.4|
|002-r0-ur5e_coordinated_move-C256|False|False|None|2|329|1|0|67.4|
|003-r0-ur5e_coordinated_move-L256|False|False|None|2|329|1|0|43.5|
|004-r0-ur5e_coordinated_move-L512|False|True|None|5|1288|1|0|172.8|
|005-r0-ur5e_suppressed_command-L1024|True|False|FAILURE|5|1275|0|0|168.3|
|006-r0-ur5e_suppressed_command-C256|False|False|None|2|329|1|0|41.4|
|007-r0-ur5e_suppressed_command-L256|False|False|None|2|329|1|0|41.0|
|008-r0-ur5e_suppressed_command-L512|False|False|None|4|1101|1|0|144.9|
|009-r0-ur5e_suppressed_command-R256|False|False|None|7|1176|3|2|152.6|
|010-r0-ur5e_missing_sensor-C256|False|False|None|8|997|0|0|127.9|
|011-r0-ur5e_missing_sensor-L256|True|False|UNKNOWN|7|892|0|0|118.0|
|012-r0-ur5e_missing_sensor-L512|True|False|UNKNOWN|5|589|0|0|77.2|
|013-r0-ur5e_missing_sensor-R256|True|False|UNKNOWN|8|1051|0|0|136.6|
|014-r0-ur5e_missing_sensor-L1024|True|False|UNKNOWN|7|848|0|0|105.0|
|015-r0-ur5e_partial_trajectory-L256|False|False|None|2|329|1|0|41.0|
|016-r0-ur5e_partial_trajectory-L512|True|False|FAILURE|7|1190|0|0|154.5|
|017-r0-ur5e_partial_trajectory-R256|False|False|None|4|841|3|2|105.1|
|018-r0-ur5e_partial_trajectory-L1024|False|False|None|5|772|0|0|180.2|
|019-r0-ur5e_partial_trajectory-C256|False|False|None|2|329|1|0|65.8|
|020-r1-ur5e_partial_trajectory-L1024|True|False|FAILURE|5|1265|0|0|169.9|
|021-r1-ur5e_partial_trajectory-R256|False|False|None|6|1099|3|2|144.7|
|022-r1-ur5e_partial_trajectory-L512|False|False|None|2|585|1|0|73.0|
|023-r1-ur5e_partial_trajectory-L256|False|False|None|2|329|1|0|40.5|
|024-r1-ur5e_partial_trajectory-C256|False|False|None|2|329|1|0|41.3|
|025-r1-ur5e_missing_sensor-C256|True|False|UNKNOWN|5|549|0|0|68.0|
|026-r1-ur5e_missing_sensor-L1024|False|False|None|8|988|0|0|121.4|
|027-r1-ur5e_missing_sensor-R256|True|False|UNKNOWN|5|605|0|0|74.4|
|028-r1-ur5e_missing_sensor-L512|False|False|UNKNOWN|8|1011|0|0|131.8|
|029-r1-ur5e_missing_sensor-L256|True|False|UNKNOWN|5|596|0|0|80.4|
|030-r1-ur5e_suppressed_command-L256|False|False|None|2|329|1|0|40.9|
|031-r1-ur5e_suppressed_command-C256|False|False|None|2|329|1|0|41.7|
|032-r1-ur5e_suppressed_command-L1024|True|False|FAILURE|6|1193|0|0|165.7|
|033-r1-ur5e_suppressed_command-R256|False|False|None|4|841|3|2|109.7|
|034-r1-ur5e_suppressed_command-L512|True|False|FAILURE|6|1118|0|0|161.0|
|035-r1-ur5e_coordinated_move-L512|False|True|None|5|707|0|0|180.4|
|036-r1-ur5e_coordinated_move-L256|False|False|None|2|333|1|0|69.4|
|037-r1-ur5e_coordinated_move-C256|False|False|None|2|329|1|0|44.5|
|038-r1-ur5e_coordinated_move-L1024|True|True|SUCCESS|6|1173|0|0|164.2|
|039-r1-ur5e_coordinated_move-R256|False|True|SUCCESS|8|1152|2|2|180.2|

## Response behavior

The independent JSON records visible prose characters and serialized tool-argument characters per trial. These are not token attribution: tool names, wrappers, provider formatting and tokenizer differences prevent equating character ratios with exact token costs. Raw responses, finish metadata and usage remain in evidence.json/trace.json. Token, character and length-stop counts omit any unreturned interrupted response and are lower bounds where usage_complete=False. Its finish reason is unknown; do not invent another length stop. Requested output allowance supplies a conservative token upper bound. Post-timeout model unload time is archived separately, outside per-trial inference latency.

## Limits and next decisions

Report successful healthy movement separately from truthful FAILURE/UNKNOWN handling. Lower tokens/time from stopping early are not an efficiency improvement. A larger output allowance is a serving change, concise instructions a prompt change, and recovery a framework intervention; no combination was tested. These cases and observations were already known, so this diagnoses a mechanism rather than demonstrating generalization. Full-precision sensor noise/timestamps, only two repetitions and sequential local execution limit causal/statistical conclusions. Do not replace the frozen256-token scores or infer model incapability from one serving profile.

Per the prospective screen, a candidate needs both healthy repetitions correct, no paired fault-outcome deterioration and no increased unsupported claims; report costs even if this screen is met. Any retained candidate needs broader fresh validation. Continue to defer model replacement, JTVR and episodic memory pending these findings.

## Audit and reproduction

The source freeze includes exact code/protocol/schedule and operator scripts. Four fresh deterministic controls passed before live inference. All persisted Phoenix ID sets must match local spans; closed trees/callback/native/model counters and generated-token caps are independently checked. Independent final state/report scoring is recomputed without editing original scores. Earlier ZIP hashes are checked. No selective reruns or online prompt tuning.

Audit errors: []
