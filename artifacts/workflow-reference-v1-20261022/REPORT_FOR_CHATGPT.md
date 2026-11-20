# Common observation-reference reporting and UR5e transfer

Prospective engineering/integration pilot; previous failed Qwen gate is unchanged.

| Phase | Backend | Condition | Correct / completed | Calls | Output tokens | Native | Invalid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| mock | ollama | model | 4/4 | 26 | 2728 | 15 | 3 |
| mock | ollama | program | 4/4 | 12 | 986 | 14 | 0 |
| mock | siwc | model | 4/4 | 18 | 474 | 10 | 0 |
| mock | siwc | program | 4/4 | 9 | 283 | 11 | 0 |
| gazebo | ollama | model | 3/4 | 18 | 2083 | 6 | 4 |
| gazebo | ollama | program | 4/4 | 14 | 1455 | 12 | 4 |
| gazebo | siwc | model | 4/4 | 19 | 660 | 11 | 0 |
| gazebo | siwc | program | 4/4 | 8 | 240 | 10 | 0 |

```json
[
  {
    "phase": "mock",
    "backend": "ollama",
    "status": "COMPLETE",
    "completed": 8
  },
  {
    "phase": "mock",
    "backend": "siwc",
    "status": "COMPLETE",
    "completed": 8
  },
  {
    "phase": "gazebo",
    "backend": "ollama",
    "status": "COMPLETE",
    "completed": 8
  },
  {
    "phase": "gazebo",
    "backend": "siwc",
    "status": "COMPLETE",
    "completed": 8
  }
]
```

Mock gate: {'pass': True, 'required_correct_trials': 16}.

Correct fault outcomes may be FAILURE or UNKNOWN; they are not successful movements. The program retrieves report values from a cited existing observation; the model supplies classification. This is combined-system performance. No old trial was rescored.

Native operations, invalid attempts and token costs are reported alongside model calls. Qwen has a hard requested output budget; Sol has an observed stopping threshold, not a hard generation cap. Censored usage must not be treated as zero.

These fresh cases are development-informed and single-repetition. No statistical, general reliability or collision-safety claim follows. Before a larger experiment, include a comparable macro-skill reference and held-out tasks/repetitions.
