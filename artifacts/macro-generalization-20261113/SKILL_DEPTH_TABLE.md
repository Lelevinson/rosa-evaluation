# G1 skill and nominal depth proposal

**Draft; not an executable catalogue or a confirmed design.** Native counts meter physical source acquisitions, not model calls.

| Domain / ID | Kind | Native depth | Intended primitive min-max calls | Actual public-API nominal min-max | Proposed calls / native / attempts | Read dependence |
|---|---|---:|---|---|---|---|
| arm / arm.cedar | inspection | 1 | 3-3 | 3-3 | 7 / 5 / 14 | independent |
| arm / arm.quartz | inspection | 2 | 3-4 | 3-3 | 8 / 6 / 16 | independent |
| arm / arm.ember | inspection | 4 | 3-6 | 3-3 | 10 / 8 / 20 | independent |
| arm / arm.lumen | inspection | 6 | 3-8 | 3-3 | 12 / 10 / 24 | independent |
| arm / arm.cobalt | movement | 3 | 5-5 | 5-5 | 9 / 7 / 18 | Prerequisite reads independent; conditional write depends on all; verification depends on write. |
| arm / arm.umber | movement | 5 | 5-7 | unsupported | 11 / 9 / 22 | Prerequisite reads independent; conditional write depends on all; verification depends on write. |
| base / base.zephyr | inspection | 1 | 3-3 | 3-3 | 7 / 5 / 14 | independent |
| base / base.jasper | inspection | 2 | 3-4 | 3-3 | 8 / 6 / 16 | independent |
| base / base.mica | inspection | 4 | 3-6 | 3-3 | 10 / 8 / 20 | independent |
| base / base.onyx | inspection | 6 | 3-8 | 3-3 | 12 / 10 / 24 | independent |
| base / base.sable | movement | 3 | 5-5 | 5-5 | 9 / 7 / 18 | Prerequisite reads independent; conditional write depends on all; verification depends on write. |
| base / base.nova | movement | 5 | 5-7 | unsupported | 11 / 9 / 22 | Prerequisite reads independent; conditional write depends on all; verification depends on write. |

The intended ranges assume exactly one tool per model response, one selection and one terminal report. Inspection min=3, max=d+2; healthy movement min=5, max=p+4 (start off target). Macro nominal model calls=2: select/bundle, then report. Errors and recovery are outside nominal minima/maxima but inside budgets.

Current inspections always acquire every selected source group in one read/verify call in either condition. Thus actual nominal primitive calls=3 for every inspection depth: native depth increases but model decision depth does not. Replacing those source groups with hidden transport reads would not create the proposed experiment.

For each domain the first four IDs cover source prefixes of length1,2,4,6; the names contain no depth labels. The last two IDs are fixed numeric targets with proposed p=1 and p=3. The public M4 state catalogue can represent the targets, but cannot represent the p=3 guard/acquisition contract. No extra catalogue descriptions or prerequisite keys were silently injected into the public schema. See skills-and-depths.json for public-schema proposals and separately labelled unsupported prerequisites.
