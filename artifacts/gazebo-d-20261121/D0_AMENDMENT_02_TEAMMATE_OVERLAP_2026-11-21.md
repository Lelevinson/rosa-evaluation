# D0 Amendment 02 (2026-11-21): overlap with teammates' work

Owner instruction, 2026-11-21. D0_PROTOCOL.md stays frozen. No change to cases, bounds, schedule, predictions,
scorer or analysis.

**Source:** teammates' reported evidence in Lelevinson/rosa-contexts (public), `origin/member/levinson` at `87eb2bd`
and `origin/member/krln` at `8072aaf`. **Reported by the teammates; not verified by us.**

| Topic | Classification | Record |
|---|---|---|
| Gazebo D | **NEW** | Levinson's Gazebo stage is Nav2/TurtleBot read-then-act with a different method (method M). There is no overlap with UR5e macro vs primitives. |
| Macro verification | **CONSISTENT** | Levinson's report-gate screen found 0 claim/final-state contradictions in 128 dev action episodes. D reports must **not** claim the macro catches false reports. Its supported value is call efficiency (D-P1), with correctness only as a non-inferiority guard (D-P3). |
| Argument handling | **ADJACENT** | Levinson's team uses no argument coercion in any arm. D adds none. ChatOllama's existing shallow JSON-decoding of string arguments (also in M4/G1) is reported as SDK assistance. |

Future work (adds to D0 §12): reuse Levinson's original-ROSA baseline harness to add a stock-ROSA arm to the
macro comparison.
