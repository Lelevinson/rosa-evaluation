# Revised skills and nominal paths

**Expected counts only. Stage 1 structural checks have not run.**

| ID | Native depth | Primitive model turns | Macro model turns | Primitive public tools | Macro public tools |
|---|---:|---:|---:|---|---|
| arm.cedar | 1 | 3 | 2 | select_skill → read_state(all selected source groups) → submit_report | select_skill -> verify_outcome(all selected source groups) → submit_report |
| arm.quartz | 2 | 3 | 2 | select_skill → read_state(all selected source groups) → submit_report | select_skill -> verify_outcome(all selected source groups) → submit_report |
| arm.ember | 4 | 3 | 2 | select_skill → read_state(all selected source groups) → submit_report | select_skill -> verify_outcome(all selected source groups) → submit_report |
| arm.lumen | 6 | 3 | 2 | select_skill → read_state(all selected source groups) → submit_report | select_skill -> verify_outcome(all selected source groups) → submit_report |
| arm.cobalt | 3 | 5 | 2 | select_skill → read_state → write_state → verify_outcome → submit_report | select_skill -> read_state/conditional write_state/verify_outcome → submit_report |
| base.zephyr | 1 | 3 | 2 | select_skill → read_state(all selected source groups) → submit_report | select_skill -> verify_outcome(all selected source groups) → submit_report |
| base.jasper | 2 | 3 | 2 | select_skill → read_state(all selected source groups) → submit_report | select_skill -> verify_outcome(all selected source groups) → submit_report |
| base.mica | 4 | 3 | 2 | select_skill → read_state(all selected source groups) → submit_report | select_skill -> verify_outcome(all selected source groups) → submit_report |
| base.onyx | 6 | 3 | 2 | select_skill → read_state(all selected source groups) → submit_report | select_skill -> verify_outcome(all selected source groups) → submit_report |
| base.sable | 3 | 5 | 2 | select_skill → read_state → write_state → verify_outcome → submit_report | select_skill -> read_state/conditional write_state/verify_outcome → submit_report |

All ten definitions use only StateSkill or InspectionSkill, registered through CapabilityRegistry. There are5 skills/domain and10 combined. Skill IDs have no depth labels. Source groups each reserve a separate native operation through the unchanged API. No extra catalogue descriptions are added.

Healthy initially off-target movement:3 native operations,5 primitive turns versus2 macro turns. Missing current pose: expected read then UNKNOWN/no dispatch,3 primitive turns versus2 macro turns,1 native attempt. Read-only unavailable/false observations can be reported directly; no automatic continuation is added. Clarification expects1 model response and0 native operations. These are proposed reference paths, not live performance results.

p3 write anchors, selective acquisition and horizon-dependent reliability are deferred to G2.
