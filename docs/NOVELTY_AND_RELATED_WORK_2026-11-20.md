# Novelty and related work — Improved ROSA bounded macro

Date: 2026-11-20. Literature search only; no model runs or experiments.
Method: web search plus opening each cited page (arXiv abstract or HTML page). For most
papers only the **abstract page** was read. Those rows are marked *(abstract)*. The full
text was read for ROSA, MetaTool/ROS, ROSClaw and BT-Agent *(full text)*. The last two were
added in a same-day revision after reviewer feedback. Claims about methods are
limited to what those pages say. Sources found only in search results and not opened are
listed separately as unverified, and are not used for any claim.

## 1. What our component is (for comparison)

The LLM selects one registered skill from a fixed, application-authored catalogue and later
classifies the evidence in a constrained report. Python then performs that skill's routine
reads, at most one conditional write, and a fresh verification. The comparison condition
("primitives") exposes the same five tools and lets the model call
`read_state`/`write_state`/`verify_outcome` itself. The implementation lives inside NASA-JPL
ROSA (LangChain ReAct). It was evaluated in Gazebo (M4, UR5e arm) and in two mock domains
(G1, arm and mobile base). Five backends were tested, including small local Q4 models via
Ollama.

## 2. Related work

| Work | What it does | Overlap with our macro | What we do differently |
|---|---|---|---|
| **SayCan** (Ahn et al., 2022) *(abstract)* | LLM proposes skills from a pretrained skill library; value functions ground feasibility | LLM chooses among predefined robot skills | Nothing conceptually new about "LLM picks a skill". Our difference is engineering: skills are deterministic read/write/verify routines inside ROSA, and we measure LLM-call cost |
| **Code as Policies** (Liang et al., 2022) *(abstract)* | LLM writes Python policy code that calls perception/control primitive APIs | Composes primitives outside per-step LLM turns | We do not generate code; routines are pre-authored and bounded (≤1 write). Less flexible, more auditable |
| **ProgPrompt** (Singh et al., 2022) *(abstract)* | Program-like prompts listing available actions and objects; LLM generates executable plans | Structured action space for the LLM | Same as above: no plan generation; one skill per invocation |
| **Voyager** (Wang et al., 2023) *(abstract)* | Ever-growing library of executable code skills, retrieved and composed (Minecraft) | Reusable executable skills | Our catalogue is fixed and hand-authored; no learning or composition |
| **ReWOO** (Xu et al., 2023) *(abstract)* | Plans tool use up front, detached from observations; reports ~5× token efficiency | Reduces repeated LLM processing between tool calls | Our saving comes from removing model turns inside a known routine, not from planning ahead. The mechanism is related, and the effect (fewer tokens/calls) is the same kind |
| **LLMCompiler** (Kim et al., ICML 2024) *(abstract)* | Planner + parallel executor of function calls; up to 3.7× latency and 6.7× cost reduction vs ReAct | Fewer sequential LLM round-trips than ReAct | We do not parallelise or plan; bundling is fixed per skill |
| **CodeAct** (Wang et al., ICML 2024) *(abstract)* | Executable Python as a unified action space; up to 20% higher success than JSON/text actions | Several tool operations per model action | Same contrast as Code as Policies |
| **AWO meta-tools** (Abuzakuk et al., Jan 2026) *(abstract)* | Mines recurring tool-call sequences from traces into "deterministic, composite tools that bundle multiple agent actions into a single invocation"; up to 11.9% fewer LLM calls, up to +4.2 pp success | **Very close mechanism**: deterministic composite tool that skips intermediate LLM reasoning | Ours are hand-authored, not mined; robotics/ROS domain with physical/mock verification; larger per-task call reduction (~39–47%) but in a narrow, designed catalogue. Not a new mechanism |
| **PyRUA-Lean** (Si et al., Oct 2026) *(abstract)* | Robot VLM agent writes Python cells that compose primitives, check results and retry; vs standard tool calling with same planner: 49% fewer LLM calls, 65% fewer input tokens on jointly solved instances, +8.6 pp success | **Very close result shape**: robot agent, primitives vs composition, matched-success call/token accounting | Ours uses pre-authored routines, not model-written code, inside ROSA with small local models and ROS 2. Their call-saving size is similar to ours |
| **Speculative Macro Commit** (Liu et al., Sep 2026) *(abstract)* | Mined macros executed speculatively by a small drafter, committed when the large actor agrees; latency gains on τ²-Bench/AppWorld | "Macro" of multiple actions | Different goal (latency via speculation); not robotics |
| **AgentPRO** (Ren & Wang, Oct 2026) *(abstract)* | Compiler-style merging of planned steps into fewer model requests; −41.85% tokens on AppWorld | Merges steps to cut model requests | Not robotics; automatic, not hand-authored |
| **BT-Agent** (Hübel et al., Oct 2026) *(full text)* | LLM selects one predefined behaviour-tree skill per decision; a supervisor BT runs it, rechecking guards/preconditions every tick, and returns structured failure feedback. Qwen3.5 NVFP4 4B/9B/27B/122B; 9B onboard (Jetson Thor) on a quadruped; Habitat. 50-task primary suite used for development, 111-task transfer suite with weights unchanged; three paired seeds per task. +5–10 pp vs Act/ReAct. Reports success and output tokens per episode (median/P99); **no LLM-call or decision counts, no per-task latency**. ROS not stated | **Very close architecture and evaluation style**: small quantized Qwen selects bounded skills; deterministic layer enforces conditions; dev/transfer split with repeated seeds | Their baselines (Act, ReAct) **share the same skill layer**, so they compare reasoning styles, not skills vs primitives. No postcondition verification step (outcome checking left to the agent). Ours: primitives vs macro on the same tool surface, inside ROSA, program-owned fresh verification, call/token/native-operation accounting. They run repeated seeds; **we do not** |
| **ALRM** (dos Santos et al., Jan 2026) *(abstract)* | Robot manipulation agent comparing Tool-as-Policy (ReAct tool loop) vs Code-as-Policy over 10 LLMs, 56 tasks | Execution-mode comparison across many models | Different modes (code generation); not ROSA; abstract gives no call counts |
| **SoK: Agentic Skills** (Jiang et al., Feb 2026) *(abstract)* | Defines skills as callable modules with applicability conditions, execution policies and termination criteria, distinct from atomic tool calls | Conceptual framing of what we built | Survey; we are an instance of its "skill" category |
| **ROSA** (Royce et al., IEEE Aerospace 2025) *(full text)* | LangChain ReAct agent over ROS1/ROS2 tools; qualitative demos; proposes but does not report metrics; lists hallucination, need for "output validation", latency and prompt reliability as limitations | Our base system | We add a bounded execution/verification layer and the first quantitative call/correctness evaluation we have found **of our own modification**. ROSA reports no success rates or call counts |
| **MetaTool-enhanced ROS** (Mahmud et al., Sep 2026) *(full text)* | Inside a ROS/ROSA-style pipeline, the LLM first writes a pseudo-code tool plan; execution is restricted to the planned tool. vs vanilla ROSA on open models (GPT-OSS via Groq), Gazebo + real robot: repeated calls 19.0%→6.1%, invalid calls 21.7%→8.1%, success 57.5%→75% (40 hardware trials) | **Closest ROSA-specific work**: modifies ROSA to tame tool-call instability of open models; vanilla ROSA baseline | Their plan is LLM-generated with no described outcome verification; they report token distributions (Fig. 5) but no LLM-call counts. Ours is program-owned, has fresh verification, and counts calls/tokens/native operations. Their study has a vanilla-ROSA baseline; **ours does not** |
| **ROSClaw** (Cardenas et al., Mar 2026) *(full text)* | Model-agnostic executive layer for ROS 2: eight tools, **each mapping to one ROS 2 primitive** (no macros/composite skills), pre-execution validation against a safety envelope, audit logging. Matched 2×2 comparison with ROSA (GPT-5.2, TurtleBot3, 20 structured + 10 safety tasks, N=10 each): completion 84.0% vs 75.5% (bounds visible), 82.5% vs 73.0% (hidden); out-of-policy rate 9–12% vs 14–22%. Reports per-turn LLM latency 1.3–2.3 s for ROSClaw only; **no LLM-call, tool-call or token totals**. No in-run outcome verification (scoring uses audit logs/odometry) | Executive layer between LLM and ROS; a **matched comparison against stock ROSA** | Opposite design choice: one tool per primitive with validation, not bundled skills. No call accounting. Their stock-ROSA comparison is something **we lack** |
| **ROSBag MCP Server** (Fu et al., Nov 2025) *(abstract)* | Tests tool calling of 8 LLMs on ROS bag analysis; large capability gap; success depends on schema, argument count and number of tools | Small/open-model tool-call reliability in ROS | Matches our Granite/Llama integration-failure finding in kind; ours is a task-execution setting |
| **AI Agents That Matter** (Kapoor et al., 2024) *(abstract)* | Argues for cost-controlled, jointly cost/accuracy evaluation, proper holdouts and reproducibility | Methodology: we report cost alongside accuracy, with a dev/held-out split | We follow this; nothing new |
| **τ-bench** (Yao et al., 2024) *(abstract)* | Scores agents by final database state vs annotated goal; pass^k reliability across repeated trials | Outcome-state scoring; reliability framing | We score independent postconditions too. We do **not** report pass^k (one run per case/condition in G1) |

Methodology items (d) with **no agent-specific source opened**: matched-pair cost accounting
and censoring of infrastructure failures. These are standard statistical practice (paired
designs; right-censoring in survival analysis). I did not find and open an agent-evaluation
paper that formalises them, so no citation is given.

## 3. Verdict: **a narrow niche is open** — the mechanism is well covered

Evidence:
- **The mechanism is not new.** Several sources describe it: "LLM selects a skill, deterministic
  code executes it", "bundle tool calls to cut LLM calls" and "composition beats one primitive
  per turn". These include SayCan, ReWOO, LLMCompiler and CodeAct (2022–2024), and in 2026 AWO
  meta-tools ("deterministic, composite tools"), PyRUA-Lean (49% fewer calls in robots) and
  BT-Agent (small onboard model selecting bounded BT skills). Our call saving (~39–47%) is in
  the same range PyRUA-Lean reports.
- **Inside ROSA, related work now exists.** The MetaTool paper modifies a ROSA-style
  pipeline for open models and compares it against vanilla ROSA. ROSClaw benchmarks against ROSA. So
  "related work exists but not inside ROSA" is **not** accurate any more.
- **What remains open is narrow, and narrower after full-text reading:** BT-Agent already
  combines small quantized Qwen models, bounded skills, a development/transfer split and
  repeated seeds. So a dev/held-out protocol and small local models are **not** distinguishing
  on their own. None of the four closest papers (MetaTool/ROS, ROSClaw, BT-Agent, PyRUA-Lean)
  reports the following together:
  (i) a direct **skills-vs-primitives** comparison on the same tool surface (BT-Agent's baselines
  share its skill layer; ROSClaw is one-tool-per-primitive; PyRUA-Lean compares model-written code);
  (ii) **LLM-call counts** together with token and native-operation accounting, in all-attempt and
  matched-success views (only PyRUA-Lean counts calls, outside ROS/ROSA);
  (iii) **program-owned post-action verification** inside ROSA (none of the three ROS-side papers
  describes an in-run postcondition check);
  (iv) prospectively frozen predictions with infrastructure-failure censoring.
  That combination is an evaluation/engineering contribution, not a mechanism.

Full texts of MetaTool/ROS, ROSClaw and BT-Agent were read (2026-11-20). ROSClaw contains no call
counts. What would still overturn this: a paper that evaluates deterministic skill macros inside
ROSA against primitives with call accounting. Full texts of AWO, PyRUA-Lean and the other 2026
papers were not read.

**Biggest weakness this search exposes:** two papers (MetaTool/ROS and ROSClaw) compare against
**stock ROSA**. We do not. Our reference is a repaired shared framework with the same five tools.
Adding that baseline would need new runs, which are not authorized. The report's limitations
section should say this plainly and cite MetaTool/ROS as the example; expect examiners to ask.

## 4. Defensible contribution claims

Your draft, checked against the search and the project's own evidence:

> "We do not claim algorithmic novelty. The contribution is a reusable bounded component for ROSA
> and a careful, pre-registered evaluation of its efficiency/reliability trade-offs across models
> and two domains, including the finding that savings track model turns, not native depth."

Problems:
1. **"pre-registered"** overstates it. Predictions were frozen internally before held-out runs
   (P1′–P6 on 2026-11-14; H-write before the three added models). But they were amended after
   dev data, are not on a public registry, the cases are AI-authored, and three backends were
   added after Sol/Qwen results were seen.
2. **"efficiency/reliability trade-offs"** is fine. Reliability evidence is mixed: M4 Qwen went
   15/20 → 14/20, while G1 favoured macro. Don't let the sentence imply a reliability gain.
3. **"two domains"** — G1's two domains are **mock** arm/base worlds. Gazebo evidence is a
   single UR5e arm (M4).
4. **"the finding that savings track model turns, not native depth"** — this was *predicted
   by design*. The primitive `read_state` bundles all sources, so the expected sequence is
   3 vs 2 turns at every depth. P1′ (formally Sol-only) came out **Support**. Present it as a
   confirmed design consequence and an important caveat for anyone expecting depth-scaling
   savings, not as a surprising discovery.

Suggested wording:

> We do not claim algorithmic novelty: letting an LLM select a skill that deterministic code
> executes, and bundling tool calls to save LLM calls, are established ideas (e.g. SayCan,
> LLMCompiler, AWO meta-tools, BT-Agent). Our contribution is engineering and evaluation:
> a reusable bounded-skill component for NASA-JPL ROSA in which the LLM selects one registered
> skill and Python performs its reads, at most one write and a fresh verification. We evaluate
> it against model-managed primitives on the same tool surface. The evaluation uses predictions
> frozen before held-out runs, all-attempt and matched-success cost accounting, and
> infrastructure-failure censoring. It covers one hosted and four local backends, in Gazebo (one
> arm) and two mock domains. LLM calls fell by 39–47% for every backend with working
> tool calls (all-attempt: Sol 41%, Qwen 39%, Ministral 46%). The saving is per model turn (≈3→2 for inspection, ≈5→2 for writes) and does not
> grow with native acquisition depth, because the primitive baseline already batches reads.
> Correctness effects were mixed and small, and are not established as a reliability gain.

## 5. Claims we must NOT make

| Claim | Why not |
|---|---|
| A new algorithm or novel mechanism | AWO, PyRUA-Lean, BT-Agent, LLMCompiler, ReWOO and SayCan cover the mechanism |
| First work to improve/benchmark ROSA | MetaTool/ROS (vs vanilla ROSA) and ROSClaw (parity protocol vs ROSA) exist |
| Better than (stock) ROSA | We never ran unmodified ROSA as a baseline. Our reference is a repaired shared framework with the same five tools. MetaTool/ROS and ROSClaw both did run a stock-ROSA baseline, which makes this gap conspicuous |
| Improves reliability | M4 Qwen 15/20 → 14/20; G1 gains are small, grouped, AI-authored and confounded with condition wording |
| Generalizes to new tasks/robots | AI-authored, reused cases; mock domains; one Gazebo arm; no physical robot |
| Small models reach parity with Sol | Qwen 26/36 → 30/36 and Ministral 28/36 → 33/36 vs Sol 33/33 → 36/36; different hardware/provenance |
| Fewer calls means less robot work | Native operations rose (Ministral 102 → 127, Qwen 100 → 106 all-attempt) |
| Savings grow with task depth | The opposite was predicted and supported (P1′); the original depth-growth idea (Stage 0 P1) was dropped before testing |
| Granite/Llama show the macro doesn't help | Those are tool-call integration failures (0 native calls / schema errors), not macro evidence |
| Reliability across repeated runs (pass^k) | Each case/condition ran once in G1 |
| Independent / externally validated human review | One teammate reviewer, self-attested eligibility |

## 6. References (opened)

1. Ahn et al. *Do As I Can, Not As I Say: Grounding Language in Robotic Affordances.* 2022. https://arxiv.org/abs/2204.01691
2. Liang et al. *Code as Policies: Language Model Programs for Embodied Control.* 2022. https://arxiv.org/abs/2209.07753
3. Singh et al. *ProgPrompt: Generating Situated Robot Task Plans using Large Language Models.* 2022. https://arxiv.org/abs/2209.11302
4. Wang et al. *Voyager: An Open-Ended Embodied Agent with Large Language Models.* 2023. https://arxiv.org/abs/2305.16291
5. Xu et al. *ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models.* 2023. https://arxiv.org/abs/2305.18323
6. Kim et al. *An LLM Compiler for Parallel Function Calling.* ICML 2024. https://arxiv.org/abs/2312.04511
7. Wang et al. *Executable Code Actions Elicit Better LLM Agents (CodeAct).* ICML 2024. https://arxiv.org/abs/2402.01030
8. Abuzakuk et al. *Optimizing Agentic Workflows using Meta-tools.* 2026. https://arxiv.org/abs/2601.22037
9. Si et al. *Fewer Tokens, Better Action: GPT-6 Astra Robot Agents with 14% Higher Success Rate but 65% Fewer Tokens.* 2026. https://arxiv.org/abs/2610.01939
10. Liu et al. *Speculative Macro Commit for Faster Tool-Using Agents.* 2026. https://arxiv.org/abs/2609.03236
11. Ren & Wang. *AgentPRO: Coordinating Compiler Optimizations for LLM Agent Workflows.* 2026. https://arxiv.org/abs/2611.00628
12. Hübel et al. *BT-Agent: Deploying Onboard Robot Agents with Behavior Trees and Multi-Fidelity Evaluation.* 2026. https://arxiv.org/abs/2610.13862 (full text: https://arxiv.org/html/2610.13862)
13. dos Santos et al. *ALRM: Agentic LLM for Robotic Manipulation.* 2026. https://arxiv.org/abs/2601.19510
14. Jiang et al. *SoK: Agentic Skills — Beyond Tool Use in LLM Agents.* 2026. https://arxiv.org/abs/2602.20867
15. Royce et al. *Enabling Novel Mission Operations and Interactions with ROSA: The Robot Operating System Agent.* IEEE Aerospace 2025. https://arxiv.org/abs/2410.06472 (full text: https://arxiv.org/html/2410.06472v2)
16. Mahmud et al. *Bridging Thought and Action: Taming Long-Horizon Instability in Open-Source LLM Agents with a MetaTool-Enhanced ROS Framework.* 2026. https://arxiv.org/html/2609.13335v1
17. Cardenas et al. *ROSClaw: An OpenClaw ROS 2 Framework for Agentic Robot Control and Interaction.* 2026. https://arxiv.org/abs/2603.26997 (full text: https://arxiv.org/html/2603.26997v1)
18. Fu et al. *ROSBag MCP Server: Analyzing Robot Data with LLMs for Agentic Embodied AI Applications.* 2025. https://arxiv.org/abs/2511.03497
19. Kapoor et al. *AI Agents That Matter.* 2024. https://arxiv.org/abs/2407.01502
20. Yao et al. *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains.* 2024. https://arxiv.org/abs/2406.12045

### Seen in search results but not opened (unverified, not used for claims)

- ROS-LLM (Mower et al., arXiv 2406.19741): the abstract page *was* opened. It describes an atomic-action library executed as ROS actions/services, with LLM-generated sequences/BTs/state machines. Kept out of the table only because the abstract reports no efficiency metrics. Opened URL: https://arxiv.org/abs/2406.19741
- Berkeley Function Calling Leaderboard (Patil et al.), TinyLLM (arXiv 2511.22138), Docker local tool-calling evaluation, ToolRobustBench (arXiv 2608.23635), τ²-bench (arXiv 2506.07982), SoK on agentic skills architecture (arXiv 2608.29596). Not opened.
