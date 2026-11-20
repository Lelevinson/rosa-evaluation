# Shared reporting reference and UR5e transfer: detailed review

Generated 2026-10-22T13:55:21.935592+00:00.

This is a prospective engineering/integration milestone. The earlier workflow-live-v1 Qwen 6/6→5/6 result and failed gate remain unchanged. The current common reporting contract is applied to both models and both conditions. The program supplies exact values from existing observations; the model still classifies the outcome.

No new evidence database, general planner, model training or model-specific repair was introduced. The reusable reporting implementation is reference.py, layered over existing session observations, freshness rules and report validation.

| Phase | Backend | Condition | Correct / completed | Calls | Input tokens | Output tokens | Native | Invalid | Seconds |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mock | ollama | model | 4/4 | 26 | 62110 | 2728 | 15 | 3 | 418.99 |
| mock | ollama | program | 4/4 | 12 | 25507 | 986 | 14 | 0 | 135.74 |
| mock | siwc | model | 4/4 | 18 | 30307 | 474 | 10 | 0 | 72.65 |
| mock | siwc | program | 4/4 | 9 | 14565 | 283 | 11 | 0 | 30.88 |
| gazebo | ollama | model | 3/4 | 18 | 42574 | 2083 | 6 | 4 | 322.73 |
| gazebo | ollama | program | 4/4 | 14 | 32053 | 1455 | 12 | 4 | 261.52 |
| gazebo | siwc | model | 4/4 | 19 | 36567 | 660 | 11 | 0 | 83.23 |
| gazebo | siwc | program | 4/4 | 8 | 13894 | 240 | 10 | 0 | 40.94 |

Correct FAILURE/UNKNOWN classifications are correct fault handling, not successful movements.

Mock progression gate: {'pass': True, 'required_correct_trials': 16}. Evidence audit: True.

```json
[
  {
    "phase": "mock",
    "backend": "ollama",
    "status": "COMPLETE"
  },
  {
    "phase": "mock",
    "backend": "siwc",
    "status": "COMPLETE"
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "status": "COMPLETE"
  },
  {
    "phase": "gazebo",
    "backend": "siwc",
    "status": "COMPLETE"
  }
]
```

## Independent checks and controls

Frozen source matches: True; saved trial trace/usage/cap/reference checks: 32. Exact persisted Phoenix span IDs and closed trees were checked independently.

Preflight: 8 reporting-contract checks,16 workflow checks,9 inference/design checks; eight actual scripted ROSA/Phoenix traces; four deterministic six-joint UR5e controls. Fresh deterministic controls and controller-readiness checks repeat before each live Gazebo backend.

Gazebo uses a separate read-only joint-state subscriber for independent scoring. Reset/observer/control operations are outside agent budgets and logged separately. The model/workflow cannot access private observer truth or injected-fault labels.

Faults are controlled transport-level injections: no-effect suppresses trajectory publication, while missing-observation masks the agent transport read. Gazebo continues publishing joint states for the independent observer. These are not naturally occurring controller/network/sensor outages.

Healthy goal-completion counts:

```json
[
  {
    "phase": "mock",
    "backend": "ollama",
    "program": false,
    "healthy_trials": 2,
    "correct_healthy": 2
  },
  {
    "phase": "mock",
    "backend": "ollama",
    "program": true,
    "healthy_trials": 2,
    "correct_healthy": 2
  },
  {
    "phase": "mock",
    "backend": "siwc",
    "program": false,
    "healthy_trials": 2,
    "correct_healthy": 2
  },
  {
    "phase": "mock",
    "backend": "siwc",
    "program": true,
    "healthy_trials": 2,
    "correct_healthy": 2
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "program": false,
    "healthy_trials": 2,
    "correct_healthy": 1
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "program": true,
    "healthy_trials": 2,
    "correct_healthy": 2
  },
  {
    "phase": "gazebo",
    "backend": "siwc",
    "program": false,
    "healthy_trials": 2,
    "correct_healthy": 2
  },
  {
    "phase": "gazebo",
    "backend": "siwc",
    "program": true,
    "healthy_trials": 2,
    "correct_healthy": 2
  }
]
```

## Retrospective fault-exercise diagnostic (no score changes)

A truthful FAILURE while already off target does not by itself establish that an injected ineffective command was exercised. The frozen primary score checks truthful outcome reporting; dispatch coverage below separately shows whether a write occurred. Do not credit command-failure handling where no command was tried. A stricter attempt/coverage requirement would need prospective definition in a future study.

```json
[
  {
    "phase": "mock",
    "backend": "ollama",
    "run_id": "04-mock_north_no_effect-model",
    "write_dispatched": true,
    "frozen_outcome_correct": true
  },
  {
    "phase": "mock",
    "backend": "ollama",
    "run_id": "05-mock_north_no_effect-program",
    "write_dispatched": true,
    "frozen_outcome_correct": true
  },
  {
    "phase": "mock",
    "backend": "siwc",
    "run_id": "04-mock_north_no_effect-model",
    "write_dispatched": true,
    "frozen_outcome_correct": true
  },
  {
    "phase": "mock",
    "backend": "siwc",
    "run_id": "05-mock_north_no_effect-program",
    "write_dispatched": true,
    "frozen_outcome_correct": true
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "04-gazebo_north_no_effect-model",
    "write_dispatched": false,
    "frozen_outcome_correct": true
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "05-gazebo_north_no_effect-program",
    "write_dispatched": true,
    "frozen_outcome_correct": true
  },
  {
    "phase": "gazebo",
    "backend": "siwc",
    "run_id": "04-gazebo_north_no_effect-model",
    "write_dispatched": true,
    "frozen_outcome_correct": true
  },
  {
    "phase": "gazebo",
    "backend": "siwc",
    "run_id": "05-gazebo_north_no_effect-program",
    "write_dispatched": true,
    "frozen_outcome_correct": true
  }
]
```

## Failed outcomes

```json
[
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "03-gazebo_south_move-model",
    "answer": "{\"actor\": \"model\", \"observation_id\": \"obs-a867b46437cf-1\", \"observed_values\": {\"/ur5e\": {\"elbow_joint\": 1.5700000000011773, \"shoulder_lift_joint\": -1.5699999999997416, \"shoulder_pan_joint\": 2.0933614915013345e-21, \"wrist_1_joint\": -1.5699999999970788, \"wrist_2_joint\": -1.5699999999999998, \"wrist_3_joint\": -2.740891198399669e-20}}, \"report_accepted\": true, \"status\": \"FAILURE\", \"values_supplied_by\": \"program_from_existing_observation\", \"verification_actor\": \"model\"}",
    "score": {
      "pass": false,
      "correct_skill": true,
      "requested_goal_attained": false,
      "truthful_report": true,
      "accepted_report_status": "FAILURE",
      "normal_terminal": true,
      "expected_status": "SUCCESS",
      "accepted_unsupported_selected_goal_success": false,
      "accepted_wrong_user_goal_success": false,
      "unsupported_success_attempts": 0,
      "invalid_attempts": 1,
      "dispatch_violations": [],
      "corrected_after_feedback": false,
      "program_native_operations": 0,
      "escalations": []
    },
    "validation": [
      {
        "type": "validation",
        "code": "skill_selection_required",
        "details": {
          "available_skills": [
            "inspect_north",
            "inspect_south"
          ]
        },
        "attempt": 1,
        "native_dispatch_for_rejected_call": false
      }
    ],
    "reports": [
      {
        "status": "FAILURE",
        "observed_values": {
          "/ur5e": {
            "shoulder_pan_joint": 2.0933614915013345e-21,
            "shoulder_lift_joint": -1.5699999999997416,
            "elbow_joint": 1.5700000000011773,
            "wrist_1_joint": -1.5699999999970788,
            "wrist_2_joint": -1.5699999999999998,
            "wrist_3_joint": -2.740891198399669e-20
          }
        },
        "actor": "model",
        "accepted": true,
        "verification_actor": "model",
        "after_write": 0,
        "observation_id": "obs-a867b46437cf-1",
        "values_supplied_by": "program_from_existing_observation"
      }
    ],
    "inference": {
      "calls": 4,
      "known_input_tokens": 9115,
      "known_output_tokens": 405,
      "output_upper_bound": 405,
      "usage_complete": true,
      "events": [
        {
          "call": 1,
          "status": "RETURNED",
          "requested_output_allowance": 1024,
          "usage": {
            "input_tokens": 2020,
            "output_tokens": 56,
            "total_tokens": 2076
          },
          "finish_reason": "stop"
        },
        {
          "call": 2,
          "status": "RETURNED",
          "requested_output_allowance": 1024,
          "usage": {
            "input_tokens": 2118,
            "output_tokens": 66,
            "total_tokens": 2184
          },
          "finish_reason": "stop"
        },
        {
          "call": 3,
          "status": "RETURNED",
          "requested_output_allowance": 1024,
          "usage": {
            "input_tokens": 2305,
            "output_tokens": 76,
            "total_tokens": 2381
          },
          "finish_reason": "stop"
        },
        {
          "call": 4,
          "status": "RETURNED",
          "requested_output_allowance": 1024,
          "usage": {
            "input_tokens": 2672,
            "output_tokens": 207,
            "total_tokens": 2879
          },
          "finish_reason": "stop"
        }
      ]
    }
  }
]
```

## Successful outcomes after feedback

```json
[
  {
    "phase": "mock",
    "backend": "ollama",
    "run_id": "03-mock_south_move-model",
    "codes": [
      "skill_selection_required"
    ]
  },
  {
    "phase": "mock",
    "backend": "ollama",
    "run_id": "07-mock_south_no_observation-model",
    "codes": [
      "skill_selection_required",
      "write_prerequisite_rejected"
    ]
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "00-gazebo_north_move-model",
    "codes": [
      "skill_selection_required"
    ]
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "01-gazebo_north_move-program",
    "codes": [
      "skill_selection_required"
    ]
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "02-gazebo_south_move-program",
    "codes": [
      "skill_selection_required"
    ]
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "04-gazebo_north_no_effect-model",
    "codes": [
      "skill_selection_required"
    ]
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "05-gazebo_north_no_effect-program",
    "codes": [
      "skill_selection_required"
    ]
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "06-gazebo_south_no_observation-program",
    "codes": [
      "skill_selection_required"
    ]
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "run_id": "07-gazebo_south_no_observation-model",
    "codes": [
      "skill_selection_required"
    ]
  }
]
```

## Limits and interpretation

One repetition per fresh development-informed case. This is not held-out statistical evidence or a causal comparison against old differently cased/contracted trials. Compare model-managed/program-managed arms within each backend and phase.

Calls can fall while native reads or invalid attempts rise. Failed attempts are included in aggregate costs; efficiency on successful tasks needs paired inspection. Some extra native work can also mean that the workflow attempted movement that the reference omitted; compare action coverage before calling that overhead waste. Initial local loads and simulator/controller timing limit latency attribution.

Claim-time evaluator observer reads also occur within the measured trial window; latency includes evaluation overhead. There is no normalized inference-only speedup claim here.

Qwen: same pinned Q4_K_M digest,ctx8192,temp0,seed42,thinking off,mmap on, 1024 output per call clamped to a cumulative2048 requested allowance. Sol: unchanged OAuth adapter/account defaults, observed2048 stopping threshold, not a hard generation cap. Censored usage is explicit in individual inference records.

Limits remain8 calls,180 seconds,10 native operations,one dispatched write per trial; 64 calls per phase/backend,128 per backend pipeline. No automatic inference replay. OAuth stays memory-only/manual consent, with existing renewal and final revocation. No credentials or encrypted reasoning appear in evidence.

Joint-state outcome verification does not establish collision avoidance, grasping or physical-robot safety. No physical hardware or large benchmark was launched.

Before a larger research study: introduce the strong macro-skill reference and held-out tasks/repetitions. Preserve unrelated Qwen failures as limitations; do not automatically redesign the framework around them. Full JTVR remains paused and episodic memory remains optional.

## Milestone result and recommendation

The minimal common reporting-reference implementation, focused fresh validation and bounded two-backend UR5e transfer have been completed if all four state records above are COMPLETE. The stronger macro-skill comparison and a larger held-out study have not been implemented or launched.

For the collected Gazebo results, interpret Qwen model-managed healthy failure as an execution omission with truthful reporting, not a false success or a truncated response. Its corresponding program-managed movement completed. The workflow also exercised an ineffective command that the model-managed reference did not attempt. These distinctions limit aggregate cost comparisons.

The current reporting interface is a successful engineering validation on these fresh cases, not a retrospective correction of the failed earlier pilot and not an isolated causal estimate of the interface change. Program-supplied bookkeeping is part of the combined system in BOTH current conditions.

Proceed next to the already-planned strong macro-skill reference and a carefully specified, small held-out comparison. Do not add more framework layers merely to repair every Qwen mistake. Keep the current module small and report negative findings if a simpler macro achieves the same results. Physical deployment and broad reliability/novelty claims remain unsupported.
