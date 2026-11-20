# G1 Stage 1 engineering report

Date: **2026-11-14**. Completion timestamp in the raw analysis uses UTC.

**Completed: 132/132 scripted real-adapter controls, with zero live model requests.**

These are AI-authored fixtures with scripted skill decisions. No independent teammate authorship or semantic-novelty review was obtained. This establishes execution and measurement plumbing, not model competence, generalization, or an efficiency advantage with real models.

The observer/world unit suites passed 9 tests. All 132 local audits and 132 persisted Phoenix audits passed; 5544 span IDs matched exactly with closed trees.

| Public-adapter path | Primitive turns | Macro turns | Native attempts in each condition |
|---|---:|---:|---:|
| Inspection, depth 1 / 2 / 4 / 6 | 3 | 2 | 1 / 2 / 4 / 6 |
| Healthy movement, depth 3 | 5 | 2 | 3 |

The 20 structural paths passed before the 112 case paths. All 56 fixtures were exercised in both conditions: 18 dev and 38 held-out-designated cases. Held-out designation concerns future live evaluation; engineering fixtures and expected results were visible during construction. There are 8 dev template groups and 13 held-out groups, including **6 held-out ladder groups**. No independent held-out authorship is claimed.

Independent-observer scoring rejected actor-only records in 132/132 trials. An additional 276 counterfactual scoring checks rejected nonexistent observation references, invented values and unsupported SUCCESS for UNKNOWN outcomes. 700 observer reads were separately traced and excluded from 372 agent-native attempts.

Missing observations, known-false conditions, ineffective commands, partial commands and clarification paths passed their scripted expected contracts. Fault scoring requires actual attempted acquisition/dispatch where applicable. Clarification here uses an engineering question check; independent human intent review remains absent.

Macro/primitive inspection native-attempt ratios were 1.00 at every depth in both domains, within the predefined [0.75, 1.25] band. These counts do not demonstrate fewer native operations. The expected 3-to-2 inspection turn difference is constant across depth because primitive inspection already batches the selected sources.

| Domain | Inspection depth | Paired fixtures | Primitive native attempts | Macro native attempts | Ratio |
|---|---:|---:|---:|---:|---:|
| Arm | 1 | 4 | 4 | 4 | 1.00 |
| Arm | 2 | 4 | 8 | 8 | 1.00 |
| Arm | 4 | 4 | 16 | 16 | 1.00 |
| Arm | 6 | 4 | 24 | 24 | 1.00 |
| Base | 1 | 4 | 4 | 4 | 1.00 |
| Base | 2 | 4 | 8 | 8 | 1.00 |
| Base | 4 | 4 | 16 | 16 | 1.00 |
| Base | 6 | 4 | 24 | 24 | 1.00 |

Each cell includes one dev and three held-out-designated fixtures. The held-out ladder has **6 template groups**, not 13 independent ladder groups. These are accounting controls, with no confidence interval or statistical performance conclusion inferred from the scripted outputs.

2186 protected historical files and 13 Stage 1 frozen files remained unchanged. Original M1–M5, M4, serving/timing, Stage 0 and revision evidence were preserved.

No Qwen/Sol inference, OAuth, Gazebo, physical robot, Git commit, push or upload was used. Synthetic token counts and scripted timings are not real-model performance measurements. P1–P4 are not decided here; the Stage 1 unchanged-source engineering prerequisite is satisfied.

The 350 scripted turns used the real adapter and its existing task limits. The current positive-path controls establish observed counts within those limits; they are not a new exhaustive boundary/stress test of every limit. The scripted caller receives the intended skill as a fixture oracle, so these controls cannot establish whether either live model chooses the correct skill.

The isolated Phoenix service was stopped after persistence verification. Its database, service log and per-trial JSON exports are retained locally. No failed control, repeated trial, retry or replacement was needed in this attempt. The laptop shutdown happened before the first frozen attempt and lost no experimental outcomes.

The two partial-write dev cases and native-ratio threshold were adopted before outcomes in the Stage 1 pre-run note. The future Sol dev proposal is 18 paired cases, at most 291 charged requests including its reserve. **Stage 2 needs owner confirmation and has not started.**

Detailed evidence: [analysis](analysis.json), [frozen control plan](control-plan.json), [freeze](freeze.json), [protected inventory](protected-before.json), [unit-test log](unit-tests.log), [persisted audit](persisted-audit.json), and each trials/<id> directory. The post-run manifest records retained file hashes; its verification receipt is separate from the pre-run freeze.
