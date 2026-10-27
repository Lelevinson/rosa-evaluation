"""Build the focused M5 research report, one-page ledger and scientific figures."""
import html
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/macro-m5-20261027'
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.local/m5-matplotlib'))


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def figures(data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    folder = OUT / 'figures'
    folder.mkdir(exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 5.2), constrained_layout=True)
    metrics = [('requests', 'Total model requests', False), ('task_seconds', 'Mean task seconds', True),
               ('output_tokens', 'Known generated tokens', False), ('native_operations', 'Native operations', False)]
    for ax, (metric, title, average) in zip(axes.flat, metrics):
        x = np.arange(2)
        for index, (condition, color) in enumerate((('primitives', '#375f8a'), ('macro', '#32a798'))):
            values = [data['backends'][b]['efficiency']['all_attempts']['costs'][condition][metric] / (20 if average else 1)
                      for b in ('siwc', 'ollama')]
            bars = ax.bar(x + (index - .5) * .34, values, width=.34, color=color, label=condition)
            ax.bar_label(bars, fmt='%.1f' if average else '%.0f', fontsize=8, padding=2)
        ax.set_xticks(x, ['Sol', 'Qwen'])
        ax.set_title(title, fontsize=10)
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_ylim(0, max(p.get_height() for p in ax.patches) * 1.25)
        ax.grid(axis='y', alpha=.15)
        ax.set_axisbelow(True)
    axes[0, 0].legend(frameon=False, fontsize=8)
    fig.suptitle('M4 full schedule: 20 tasks per condition/backend; failures included', fontsize=11)
    fig.savefig(folder / 'm4_efficiency.png', dpi=180)
    fig.savefig(folder / 'm4_efficiency.pdf')
    plt.close(fig)


def ledger_rows():
    return [
        ['Reusable bounded ROSA capability component works in the tested stack.', 'M1/M2 acceptance, M3 Gazebo demo and M5 empty-target wheel probe.', 'One arm, one movement capability plus read-only readiness; existing dependencies/ROS retained.'],
        ['Sol macro reduces orchestration cost on the M4 suite.', '20/20 each;68→38 requests;328.36→194.58 task seconds.', 'No observed failures; no population-level preservation/equivalence or novel-algorithm claim.'],
        ['Qwen has conditional efficiency savings, with mixed correctness.', '15/20→14/20; both-pass13 pairs53→28 requests and50.8% less task time.', 'Failed preset screen; matched subset excludes discordant failures; no reliability gain.'],
        ['Native work is not uniformly reduced.', 'Sol38→40; Qwen50→48 all attempts,31→29 both-pass.', 'Counts mix different operation types and unsuccessful work; not energy or dollar cost.'],
        ['Grounded skill reports can answer the wrong/unresolved goal.', 'Five accepted Qwen readiness SUCCESS reports fail intent scoring.', 'Empirical examples in this system, not a new general discovery or eleven false successes.'],
        ['Visible first-action and recovery paths differ in partial-command cases.', 'Primitives reject pre-selection readiness read, then correct; macro inspection commits before attempted correction.', 'Retrospective; identical schemas/system prompt, different condition sentence; cause not isolated.'],
        ['M4 evidence is internally traceable and bounded.', '80 live audits,3,290 spans;20 controls/202 spans;250 requests; retained frozen inputs.', 'Integrity/audits are research-quality checks, not proof of task validity, novelty or physical safety.'],
        ['Clarification operator review is complete; human review is deferred.', 'Eight operator ratings; label-withheld packet prepared at user request.', 'No independent human rating or adjudication is claimed; response style may reveal source.'],
        ['The comparison isolates execution ownership within a repaired ROSA configuration.', 'Shared prompts/contracts, permissions, guards and outcome checker.', 'No untouched-upstream ROSA comparison; no attribution of the whole repair bundle’s benefit.'],
        ['Scope is short fixed-catalogue simulation tasks.', 'Ten families, two repeated cases, two backends, one six-joint UR5e.', 'No broad task/model/robot generalization, multi-skill autonomy, memory, JTVR or hardware claim.'],
    ]


def pages(data):
    import csv
    family = list(csv.DictReader((OUT / 'per-family-results.csv').open(encoding='utf-8')))
    status = load(OUT / 'status.json')
    backup = load(OUT / 'off-machine-verification.json') if (OUT / 'off-machine-verification.json').exists() else None
    package = load(OUT / 'package/acceptance.json')
    demos = {b: load(OUT / ('demo-' + b) / 'result.json') if (OUT / ('demo-' + b) / 'result.json').exists() else None for b in ('siwc', 'ollama')}
    P = lambda text: ('p', text)
    T = lambda heads, rows: ('table', heads, rows)
    B = lambda items: ('bullets', items)
    result = []
    result.append(('Reducing LLM orchestration overhead in ROSA through bounded robotic skill macros', [
        P('**Research report · 2026-10-27**'),
        P('We implemented bounded robotic skill macros within a repaired ROSA framework and evaluated '
          'them against model-managed primitive execution. On the tested catalogue, macros reduced '
          'LLM orchestration overhead while producing mixed correctness outcomes. Sol passed all20 '
          'tasks in each condition; Qwen passed15/20 with primitives and14/20 with macros. Five accepted, '
          'evidence-grounded reports failed the requested goal. The results support efficiency benefits '
          'in this environment, without establishing general reliability improvement or superiority '
          'to unmodified ROSA.'),
        T(['Backend', 'Correct: primitive / macro', 'Calls', 'Mean task seconds'], [
            ['Sol', '20/20 /20/20', '68 →38', '16.42 →9.73'],
            ['Qwen', '15/20 /14/20', '91 →53', '133.49 →85.18']]),
        ('image', 'figures/m4_efficiency.png', 460, 260),
        P('**Decision:** Sol passes the prospective engineering screen; Qwen fails its no-greater-failure '
          'criterion. Keep the module optional and bounded. Do not interpret cheaper failed tasks '
          'as reliability improvements. M5 is postprocessing/delivery, not another research campaign.'),
        P('Prepared from frozen source, saved M4 attempts and explicitly labeled retrospective analysis. '
          'Independent human clarification adjudication is deferred at the user’s request; operator '
          'ratings and a label-withheld reviewer packet are retained separately.')]))
    result.append(('1. Question, context and contribution', [
        P('The project improves the software surrounding an LLM-based robotic agent; it does not train '
          'a new model. The narrow question is whether moving predictable read/conditional-write/check '
          'steps from the model loop into bounded Python skills reduces completion cost without an '
          'observed correctness loss on this task suite.'),
        P('ROSA exposes robotic interfaces through language-model tools and is designed for extension '
          '[Royce et al., ROSA](https://arxiv.org/abs/2410.06472v2). We reuse this framework and its '
          'ecosystem. Our primitive reference already includes shared interface, reporting, tracing '
          'and resource repairs. It is not untouched upstream ROSA.'),
        P('Skill-based language interfaces and robot policy programs have substantial prior work. '
          '[SayCan](https://arxiv.org/abs/2204.01691v2) combines language with grounded robot skills. '
          '[Code as Policies](https://arxiv.org/abs/2209.07753v4) generates robot policy programs. '
          'Here the routines are pre-authored, permitted and bounded; the model selects from a small '
          'catalogue. These papers provide context, not baselines tested in our experiment.'),
        B(['Engineering deliverable: a reusable Python component integrated with actual ROSA and ROS2/Gazebo.',
           'Empirical result: measured within-backend call/token/time trade-offs against a competent shared primitive reference.',
           'Failure evidence: correct skill-level observations/reports can coexist with incorrect user-goal completion.',
           'Research quality: frozen inputs, independent observer state, exact trace matching and preserved failures support scrutiny, not novelty by themselves.']),
        P('We claim neither a new macro-action algorithm nor general capability, semantic grounding '
          'or physical safety. Prior JTVR, caching and reliability studies informed the choice but '
          'used different protocols; their denominators/effect sizes are not pooled with M4.'),
        P('The historical six-stage research plan differs from the current M1–M5 completion roadmap. '
          'M1 packaged the module; M2 added a genuinely read-only capability; M3 demonstrated model '
          'selection and failures; M4 performed the frozen comparison. M5 protects, analyzes and '
          'presents those results. Memory and original JTVR remain deferred.')]))
    result.append(('2. Component and task contract', [
        P('There is one six-joint UR5e arm, **one state-changing movement capability** with home, '
          'stage_left and park_right targets, and **one read-only readiness capability**. Four '
          'catalogue entries are not four robotic capabilities. This is not a one-actuator robot '
          'or a demonstration of chained multi-skill autonomy.'),
        T(['Public tool', 'Responsibility'], [
            ['select_skill', 'Model selects one permitted exact ID. Primitives returns targets; macro performs bounded routine.'],
            ['read_state', 'Acquire fresh permitted evidence, preserving unavailable observations.'],
            ['write_state', 'At most one necessary authorized movement with known prerequisites and exact registered targets.'],
            ['verify_outcome', 'Fresh selected-goal/readiness check, callable by model or program.'],
            ['submit_report', 'Model classifies SUCCESS/FAILURE/UNKNOWN and cites latest observation ID; program supplies/checks exact recorded values.']]),
        P('The application grants allowed skills. The model does not infer new permissions from prose. '
          'Both modes commit to one selected skill per invocation; selection in macro mode immediately '
          'runs routine operations. Incorrect selection can be locked in. Unknown/ineffective '
          'commands are not replayed, and accepted reports terminate without an extra acknowledgement.'),
        P('HOME=(0,−1.57,1.57,−1.57,−1.57,0). M4 stage_left has pan−0.14/final wrist0.20; '
          'park_right has pan0.16/final wrist−0.12. All targets stay within0.4 rad of HOME. '
          'Commands use the standard trajectory controller and three-second trajectories. '
          'Final joint tolerance is0.025 rad. Command acceptance is not physical verification.'),
        P('Readiness separately queries controller activation and fresh complete finite joint data. '
          'It has no trajectory publisher. True/false/unavailable facts use1/0/null encoding. '
          'Readiness SUCCESS requires all checks true; observed unready is FAILURE, missing evidence '
          'UNKNOWN. Readiness does not authorize motion or certify collision safety.'),
        P('Shared guards validate selected evidence/classification, not arbitrary natural-language '
          'intent. The external evaluator separately checks the requested goal and fault exercise. '
          'A model-generated prose statement is not exhaustively verified by the structured report validator.')]))
    result.append(('3. Frozen study design and resources', [
        P('Ten prospective families × two repetitions × two conditions × two backends produce80 '
          'trials:20 per condition/backend. Cases were authored by this project and frozen before '
          'inference. Repetitions are repeated cases, not independent new tasks. The four examined '
          'partial-command first inputs are identical within each condition’s repetitions.'),
        T(['Families', 'Coverage'], [
            ['Movement (five)', 'Constrained goal selection; already-satisfied goal; suppressed ineffective command; actual partial wrist command; missing movement prerequisite.'],
            ['Inspection (four)', 'Healthy readiness; actually inactive controller; missing controller observation; missing joint observation.'],
            ['Ambiguity (one)', 'Request clarification before any selection/acquisition/report. No movement permission.']]),
        P('Adjacent paired order is counterbalanced, with case rotation between repetitions and '
          'reversed condition ordering across backends. Sol runs before Qwen; simulator access is '
          'serialized. Before live execution,20 deterministic controls and their exact Phoenix '
          'audits passed. Resets, independent observations and controller fault setup are outside '
          'the task loop and separately accounted.'),
        T(['Limit', 'Value'], [
            ['Per task', '8 charged calls;2,048 observed generated tokens;10 native operations;16 tool attempts;3 permitted corrections;360 seconds;≤1 movement dispatch.'],
            ['Qwen generation', 'num_ctx8192; up to1,024 output tokens/call within remaining allowance; temperature0, seed42, mmap; no reasoning/stream/cache.'],
            ['Backend', '320 ordinary request slots+3 eligible infrastructure slots=323;8-hour ceiling, not forecast.'],
            ['Recovery', 'At most one eligible HTTP502/503/504 retry/logical call; no quota/auth/timeout/length or robot-command replay. No reserve was used.']]),
        P('Local Qwen3.5:9b Q4_K_M uses pinned Ollama0.40.6 on an RTX4050 laptop with6GB VRAM '
          'and nominal16GB RAM. Hosted gpt-6.1-sol uses the existing ChatSiwc OAuth adapter and '
          'provider defaults. Equal budgets within a backend do not imply equal hardware, '
          'tokenization or provider generation caps across models.'),
        P('Frozen source: research c0c61a0, evaluation4412f05;62 file hashes and applicable research/ '
          'Phoenix locks. Protocol and source copies remain unchanged. All250 requests have known '
          'usage; there are no censored, replaced, extended or unstarted M4 cells.')]))
    family_table = []
    for name in sorted({r['family'] for r in family}):
        values = []
        for b in ('siwc', 'ollama'):
            for c in ('primitives', 'macro'):
                row = next(r for r in family if r['backend'] == b and r['condition'] == c and r['family'] == name)
                values.append(row['primary_passes'] + '/2')
        family_table.append([name.replace('_', ' '), *values])
    result.append(('4. Correctness by family and paired outcome', [
        T(['Family', 'Sol P', 'Sol M', 'Qwen P', 'Qwen M'], family_table),
        P('P=primitives, M=macro. Passing includes the correct grounded FAILURE/UNKNOWN or '
          'clarification in the applicable case; these percentages are not physical movement '
          'success rates. A partial-command case must actually exercise the injected command.'),
        T(['Backend', 'Both pass', 'P-only', 'M-only', 'Both fail'], [
            ['Sol', '20', '0', '0', '0'], ['Qwen', '13', '2', '1', '4']]),
        P('Qwen’s one macro-only success is constrained selection repetition2. Its two '
          'primitive-only successes are partial-command repetitions1/2. The four both-fail '
          'pairs are missing movement prerequisites and ambiguous intent, each repeated twice.'),
        P('The prospective screen requires all20 pairs and audits, no dispatch violations, '
          'no greater count of primary failures,≥25% fewer calls on both-pass pairs and≤25% '
          'extra native operations on that subset. Sol passes. Qwen fails because macro has '
          'six failed tasks versus five with primitives. This gate is a development decision, '
          'not evidence of statistical harm, equivalence or population-level reliability preservation.'),
        P('Sol’s ceiling result means no failures were observed in this suite, not that unseen '
          'failure probability is zero. Qwen’s one-task difference remains uncertain at this '
          'sample size. We retain the predefined gate rather than changing it after results.')]))
    cost_tables = []
    for cohort, title in (('both_pass_pairs', 'Both-pass pairs: conditional cost of successful completion'),
                          ('all_attempts', 'All attempts: actual complete-schedule expenditure')):
        rows = []
        for b, label in (('siwc', 'Sol'), ('ollama', 'Qwen')):
            view = data['backends'][b]['efficiency'][cohort]
            for c in ('primitives', 'macro'):
                x = view['costs'][c]
                rows.append([label+' '+('P' if c=='primitives' else 'M'), str(view['pairs']), str(x['requests']),
                             f"{x['input_tokens']:,}", f"{x['output_tokens']:,}", str(x['native_operations']), f"{x['task_seconds']:,.2f}"])
        cost_tables += [P('**'+title+'**'), T(['Backend/mode', 'Pairs', 'Calls', 'Input', 'Output', 'Native', 'Task sec'], rows)]
    result.append(('5. Efficiency and elapsed time', [*cost_tables,
        P('On both-pass pairs, Sol saves44.1% calls and40.7% task time; Qwen saves47.2% calls '
          'and50.8% task time. The matched subset has20 Sol pairs but only13 Qwen pairs, '
          'excluding discordant/harder cases. All-attempt call savings are44.1% and41.8%; '
          'Qwen’s all-attempt time reduction is36.2%. Neither view replaces correctness.'),
        P('Native work is heterogeneous. Sol38→40 (+5.3%) is explained by the already-satisfied '
          'cases: primitives uses one fresh read per case, while macro uses two. Qwen50→48 '
          '(−4.0%) includes missed commands and different reads; both-pass31→29 is−6.5%. '
          'Counts are not equal-duration operations, energy or monetary charges.'),
        T(['Backend/mode', 'Mean sec', 'Median sec'], [
            [label+' '+c, f"{d['mean_task_seconds']:.2f}", f"{d['median_task_seconds']:.2f}"]
            for b,label in (('siwc','Sol'),('ollama','Qwen')) for c,d in data['backends'][b]['conditions'].items()]),
        P('Closed backend time including setup/reset/independent checks/audit/cleanup is17.68 '
          'minutes for Sol and81.97 for Qwen. Task loops account for8.72 and72.89 minutes; '
          'non-task overhead is8.96 and9.08 minutes. Waiting for the other backend is excluded. '
          'Task-loop time is not pure generation speed; backend/hardware/order differences '
          'preclude an intrinsic cross-model speed ranking. Repeated input tokens are counted '
          'per request, not unique language content or an estimate of billed dollars.')]))
    uncertainty = []
    for b,label in (('siwc','Sol'),('ollama','Qwen')):
        for metric in ('primary_difference_percentage_points','both_pass_pairs:requests_reduction_percent','both_pass_pairs:task_seconds_reduction_percent'):
            q=data['backends'][b]['family_resampling_ranges'][metric]
            short={'primary_difference_percentage_points':'Correctness difference (pp)',
                   'both_pass_pairs:requests_reduction_percent':'Both-pass call reduction (%)',
                   'both_pass_pairs:task_seconds_reduction_percent':'Both-pass time reduction (%)'}[metric]
            uncertainty.append([label,short,f"{q['low']:.1f} to {q['high']:.1f}"])
    result.append(('6. Uncertainty: descriptive evidence first', [
        P('All analysis on this page is explicitly post hoc. The ten-family table and paired '
          'outcomes carry the main interpretation. Neither repeated fixed-seed cases nor '
          'a large span count supply independent task diversity.'),
        T(['Backend', 'Metric', '95% empirical family range'], uncertainty),
        P('Resample whole families10,000 times, seed20261027, preserving both repetitions '
          'and conditions. Ranges are2.5th/97.5th percentiles, a sensitivity to the observed '
          'family mix, not calibrated guarantees for unseen tasks. Zero denominator draws '
          'are omitted per metric and counted in the JSON output.'),
        P('Sol’s zero correctness-difference range is degenerate because every observed '
          'case passed; this bootstrap cannot invent failures. It does not demonstrate '
          'noninferiority. Under an independent-binomial reference only, Wilson95 for20/20 '
          'is approximately83.9%–100%. That model ignores this study’s pairing/clustering '
          'and is neither the true design-adjusted uncertainty nor a guaranteed lower bound.'),
        P('The exact family-level sign-flip sensitivity returns p=1.0 for both backends. '
          'It assumes condition-label exchangeability/symmetry not established by the designed '
          'suite; Sol has no variation and Qwen only two families with nonzero condition '
          'differences. This is not evidence that the one-task difference is definitely noise.'),
        P('Methodological references: [NIST proportions intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) '
          'and [Cameron–Miller cluster inference](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf). '
          'Few hand-authored clusters and selected-success conditioning remain substantial '
          'limitations. No exploratory statistic changes the frozen engineering screen.')]))
    result.append(('7. Retrospective forensic review: partial-command pairs', [
        P('These four cases distinguish Qwen’s conditions: both primitive cases pass and '
          'both macro cases fail. Outcomes and some snapshots/prompts were already seen. '
          'The earlier review handoff recorded a wording hypothesis; deeper first-turn '
          'inspection is retrospective, not a blind or preregistered causal test.'),
        T(['Step', 'Primitives: both repetitions', 'Macro: both repetitions'], [
            ['Visible inputs', 'Same system prompt, five schemas, catalogue and movement request.', 'Same as primitives; user-message execution-condition sentence differs.'],
            ['First request', 'read_state(/ur5e_readiness), before selection; rejected without data.', 'select_skill(inspect_readiness); permitted, immediately executes inspection.'],
            ['Next selection', 'select_skill(park_right); accepted.', 'select_skill(park_right); rejected as already selected.'],
            ['Later behavior', 'Premature write blocked; fresh read, one partial command, verification and FAILURE report.', 'r1: FAILURE about readiness rejected, then readiness SUCCESS accepted. r2: length stop.'],
            ['Fault exercise', 'Actual injected partial wrist movement exercised twice.', 'No movement; partial-command fault never exercised.']]),
        P('Both conditions show a readiness-first initial tool request. The primitive '
          'pre-selection rejection leaves the skill choice open; the macro selection '
          'commits it. Both modes later request the correct park_right skill. Thus the '
          'records do not support an absolute claim that Qwen could not identify the '
          'movement goal. They expose different action/feedback paths under the shared '
          'one-skill rule.'),
        P('The select_skill description itself is identical across modes. There is no '
          'first-call prose in the macro choices demonstrating a belief that inspection '
          'was cheaper/safer. Later model explanations are observable text, not privileged '
          'causal access. Wording and execution/commitment interaction are plausible '
          'hypotheses; these records do not isolate why the first actions differed.'),
        P('Changing selection/commitment policy could change permissions and replay risk. '
          'No runtime repair was made and no additional diagnostic was run. Exact decoded '
          'prompts, schemas, call sequences, tool feedback and source trace hashes accompany '
          'PARTIAL_COMMAND_FORENSIC_REVIEW.md and partial-command-forensics.json.')]))
    result.append(('8. Goal truth, fault coverage and review quality', [
        P('All11 failed Qwen tasks selected readiness inspection: seven explicit movement '
          'requests and four ambiguous requests requiring clarification. Five ended with '
          'accepted grounded readiness SUCCESS, while six ended with safe error output '
          '(five length stops and one validation-retry exhaustion). These are distinct '
          'failure modes, not eleven hallucinated-success reports.'),
        P('In macro partial-command repetition1, Qwen explicitly attempts a FAILURE report '
          'after recognizing the requested movement was not performed. The validator '
          'rejects that classification because the *selected readiness skill* succeeded. '
          'The accepted replacement SUCCESS is true about readiness but does not satisfy '
          'the movement request. This illustrates the scope of skill-level verification.'),
        P('Sol exercises all required faults. Qwen’s primitive partial-command cases '
          'exercise actual partial movement; its macro counterparts and all four missing '
          'movement-prerequisite cases select inspection and miss intended fault coverage. '
          'Truthful unrelated observations are not credited as fault handling.'),
        P('All80 live local and exact persisted-Phoenix audits match3,290 spans;20 '
          'deterministic controls add202. No dispatch violations, uncertain-command replay '
          'or missing usage were observed. Both simulators cleaned up. Verification '
          'uses separate actor/evaluator state and transport instances on the same simulator '
          'and APIs, not independently authored scoring or a different physical sensor.'),
        P('All eight clarification cases have stored Codex operator ratings: four Sol '
          'passes and four Qwen failures. **Independent human review is deferred by user '
          'choice.** A packet with model/condition labels and previous scores withheld '
          'is prepared, with empty ratings and a separate operator key. Response style '
          'may reveal labels. Future human ratings/disagreements must be preserved '
          'separately, not silently substituted into frozen M4 results.'),
        P('Cryptographic archive checks establish byte identity. Trace accounting checks '
          'instrumentation completeness. Neither alone proves a correct task contract, '
          'causal explanation, broad reliability or safety.')]))
    demo_rows=[]
    for b,label in (('siwc','Sol'),('ollama','Qwen')):
        d=demos[b]
        demo_rows.append([label,'not recorded' if d is None else ('verified goal' if d['pass'] else 'failed / see record'),
                          '—' if d is None else str(d['live_model_requests']),
                          '—' if d is None else str(d.get('camera_frames',0))])
    backup_text=('Off-machine verification is recorded: '+backup.get('summary','see off-machine-verification.json') if backup else
                 'Research branch has been pushed. Evaluation publication/off-machine verification remains pending the explicit public/private destination decision after automatic approval review rejected the public retained-evidence upload. No remote evaluation backup is claimed.')
    result.append(('9. Reproducibility and delivery acceptance', [
        P('Frozen M4 inputs, scores and archives are unchanged. M5 creates separate '
          'postprocessing reports, reviewer materials, package checks and presentation '
          'recordings. Source lists/digests, exact commands, tables and scripts accompany '
          'the delivery. M4 final ZIP remains separately immutable.'),
        P('Credential checks covered intended branch history and retained evidence, '
          'including archive entries. Two exact source-file sentinel literals were reviewed '
          'as expired noncredentials; the initial finding and resolution are retained. '
          'The retained-work backup contains4,423 files, SHA256 '
          'b8ef4c05300460dcb72f218de73adec7b08599ec1d409c617eafe0c93099c580. '
          'Pattern checks cannot prove absence of all possible secrets. Protected credentials, '
          'local service databases and environments are excluded.'),
        P('The first backup filter also excluded14 historical uv.lock copies by treating all '
          '.lock files as transient. The filter is corrected, and a separately verified '
          'dependency-lock addendum preserves those copies without replacing the original '
          'backup. Current committed locks were already protected by repository history.'),
        P(backup_text),
        P('Offline build/empty-target installation passed using the existing pinned Python3.12 '
          'dependencies and ROS stack. Movement and inspection public API checks and installed '
          'CLI help passed, with no experiment imports. This is not a fresh-OS/dependency-free '
          'installation. The wheel is the modified jpl-rosa1.0.10 distribution with internal '
          'component0.2.0, not a separately published package.'),
        P('An initial smoke probe incorrectly accessed an internal operations field; its '
          'failed attempt is preserved. The corrected public snapshot probe passed without '
          'changing runtime source. A zero-model Gazebo camera preflight passed.'),
        T(['Presentation run', 'Independent outcome', 'Model requests', 'Camera frames'],demo_rows),
        P('Presentation recordings are isolated Gazebo-camera footage, not desktop capture, '
          'archived-model replays or additional M4 observations. The static camera/rendering '
          'world is an additive presentation fixture; robot/controller/guard source is '
          'unchanged. These runs are not used for efficiency inference. Edited pauses and '
          'video-speed changes must be labeled. Each model run is bounded at eight requests; '
          'failed takes are retained, not repeated to obtain a success.'),
        P('Human-review completion and remote publication status must be read from the '
          'current M5 progress record; a locally prepared ZIP or an old report does not '
          'establish either. The living master README remains the current project entry point.')]))
    result.append(('10. Discussion, conclusion and references', [
        P('The engineering benefit is reduced LLM orchestration overhead in a small, '
          'bounded ROSA configuration. Bundling removes decision points but may add '
          'native reads, commit an unsuitable skill earlier, or shift the feedback path. '
          'The working module and bounded empirical findings are useful without claiming '
          'a new algorithm. Efficiency and task correctness must be presented together.'),
        B(['No untouched-upstream ROSA comparison: only execution ownership within the repaired reference is isolated.',
           'One arm, short tasks, ten designed families, repeated fixed-serving cases and two backends limit generalization.',
           'Five wrong-goal grounded reports are empirical examples of a familiar distinction, not a universal failure rate.',
           'Operator-authored evaluator/review, deferred human adjudication and a small selected-success cohort remain limitations.',
           'No physical hardware, obstacle/path safety, grasping, perception, autonomous skill chaining or memory claim.']),
        P('No optional experiment is scheduled. A later selection diagnostic would need '
          'a specific decision-changing question and separate frozen protocol; it could '
          'test presentation sensitivity, not establish a general capability explanation. '
          'A stock-ROSA comparison is necessary for stronger upstream-superiority claims, '
          'not for the narrower measured contrast reported here.'),
        P('**Conclusion:** bounded macros reduced calls and measured task-loop time on '
          'this catalogue. Sol showed no observed failures; Qwen failed the preset '
          'reliability-preserving screen. Skill-level evidence truth did not guarantee '
          'correct user intent. These conclusions are intentionally limited to what '
          'the implementation and archived evidence establish.'),
        P('**References (primary sources; checked2026-10-27)**'),
        B(['Royce et al. Enabling Novel Mission Operations and Interactions with ROSA. [arXiv2410.06472v2](https://arxiv.org/abs/2410.06472v2).',
           'Ahn et al. Do As I Can, Not As I Say. [arXiv2204.01691v2](https://arxiv.org/abs/2204.01691v2).',
           'Liang et al. Code as Policies. [arXiv2209.07753v4](https://arxiv.org/abs/2209.07753v4).',
           'NIST/SEMATECH. [Proportion confidence intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).',
           'Cameron and Miller (2015). [A Practitioner’s Guide to Cluster-Robust Inference](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf).']),
        P('Appendices: frozen M4 protocol/evidence; full traces and retrospective extraction; '
          'family/paired/cost CSVs; exploratory analysis JSON; human-review packet/key; '
          'installation acceptance; demonstration provenance/video; backup and integrity manifests.')]))
    # Keep a ten-page report: the opening overview plus nine focused sections.
    # Fold the essential background into the component section; the ledger and
    # discussion already carry the removed page's contribution/scope statements.
    result.pop(1)
    result[1][1].insert(0, P('This work extends [ROSA](https://arxiv.org/abs/2410.06472v2) with pre-authored bounded routines. '
        '[SayCan](https://arxiv.org/abs/2204.01691v2) grounds language in robot skills; '
        '[Code as Policies](https://arxiv.org/abs/2209.07753v4) generates robot programs. '
        'These are context, not experimental baselines. Our contribution is implementation and '
        'measured trade-offs; no novel macro-action algorithm is claimed.'))
    result = [(re.sub(r'^\d+\.', str(index) + '.', heading) if index else heading, blocks)
              for index, (heading, blocks) in enumerate(result)]
    return result


def pdf_and_markdown(contents):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    import matplotlib.font_manager as fonts
    regular=fonts.findfont('DejaVu Sans')
    bold=fonts.findfont(fonts.FontProperties(family='DejaVu Sans',weight='bold'))
    pdfmetrics.registerFont(TTFont('M5Sans',regular))
    pdfmetrics.registerFont(TTFont('M5SansBold',bold))
    pdfmetrics.registerFontFamily('M5Sans',normal='M5Sans',bold='M5SansBold',italic='M5Sans',boldItalic='M5SansBold')
    body=ParagraphStyle('Body',fontName='M5Sans',fontSize=9.0,leading=12.4,spaceAfter=8,alignment=TA_LEFT)
    title=ParagraphStyle('Title',parent=body,fontName='M5SansBold',fontSize=15,leading=19,spaceAfter=13,textColor=colors.HexColor('#173c5b'))
    cell=ParagraphStyle('Cell',parent=body,fontSize=7.4,leading=9.7,spaceAfter=0)
    def fmt(text):
        text=html.escape(str(text))
        text=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',text)
        text=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',r'<a href="\2" color="#246a97">\1</a>',text)
        return text
    def table(heads,rows,width):
        data=[[Paragraph(fmt(v),cell) for v in row] for row in [heads,*rows]]
        t=Table(data,colWidths=[width/len(heads)]*len(heads),repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf4')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#b8c7d1')),
            ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        return t
    flow=[];md=[]
    for index,(heading,blocks) in enumerate(contents):
        if index:flow.append(PageBreak())
        flow.append(Paragraph(fmt(heading),title));md+=['# '+heading if index==0 else '## '+heading,'']
        for block in blocks:
            if block[0]=='p':flow.append(Paragraph(fmt(block[1]),body));md += [block[1],'']
            elif block[0]=='bullets':
                for item in block[1]:flow.append(Paragraph('• '+fmt(item),body));md.append('- '+item)
                md.append('')
            elif block[0]=='table':
                flow += [table(block[1],block[2],505),Spacer(1,10)]
                md += ['| '+' | '.join(block[1])+' |','|'+'---|'*len(block[1])]
                md += ['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in block[2]]
                md.append('')
            else:
                flow += [Image(str(OUT/block[1]),width=block[2],height=block[3]),Spacer(1,8)]
                md += ['![M4 descriptive efficiency figure]('+block[1]+')','']
    def footer(canvas,doc):
        canvas.setFont('M5Sans',8);canvas.setFillColor(colors.HexColor('#647582'))
        canvas.drawString(45,25,'ROSA bounded macros · M5 · 2026-10-27')
        canvas.drawRightString(A4[0]-45,25,str(doc.page))
    pdf=OUT/'ROSA_M5_RESEARCH_REPORT.pdf'
    SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=40,bottomMargin=42,
        title='Bounded ROSA macros: focused research report',author='ROSA project team; prepared from archived evidence').build(flow,onFirstPage=footer,onLaterPages=footer)
    (OUT/'M5_RESEARCH_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    rows=ledger_rows()
    ledger_md=['# Claim, evidence and limitation ledger','','Date: **2026-10-27**. These claims do not change the frozen M4 screen.','',
               '| Claim | Evidence | Limitation |','|---|---|---|']+['| '+' | '.join(row)+' |' for row in rows]
    (OUT/'CLAIM_LEDGER.md').write_text('\n'.join(ledger_md)+'\n',encoding='utf-8')
    ledger_flow=[Paragraph('ROSA M5: claim / evidence / limitation ledger',title),
                 table(['Claim','Evidence','Limitation'],rows,750),Spacer(1,8),
                 Paragraph('Human adjudication is deferred; stronger claims require new evidence. Backup/publication status is recorded separately.',body)]
    SimpleDocTemplate(str(OUT/'ROSA_M5_CLAIM_LEDGER.pdf'),pagesize=landscape(A4),leftMargin=45,rightMargin=45,
        topMargin=32,bottomMargin=30,title='ROSA M5 claim ledger').build(ledger_flow)


def main():
    data=load(OUT/'retrospective-analysis.json')
    figures(data)
    pdf_and_markdown(pages(data))
    from pypdf import PdfReader
    count=len(PdfReader(OUT/'ROSA_M5_RESEARCH_REPORT.pdf').pages)
    ledger_count=len(PdfReader(OUT/'ROSA_M5_CLAIM_LEDGER.pdf').pages)
    assert count==10, f'report_page_count:{count}'
    assert ledger_count==1, f'ledger_page_count:{ledger_count}'
    print(json.dumps({'research_report_pages':count,'claim_ledger_pages':ledger_count,'new_research_trials':0}))


if __name__=='__main__':main()
