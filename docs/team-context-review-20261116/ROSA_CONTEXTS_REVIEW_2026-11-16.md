# ROSA team context repository: review and implications

Review began **2026-11-16**; documentation closeout **2026-11-17**.
The filename and snapshot directory retain the review's start date.
Reviewer: **Codex, Martin's implementing assistant**.
Scope: contextual/document review and offline integrity/arithmetic checks. No
independent reproduction of Levinson's research, runtime integration or new experiment.

**Assessment:** the owner's interpretation is correct: `rosa-contexts` shares
team research context. ChatGPT's main interpretation is supported. The repo
does not itself optimize an agent's inference context. It provides useful
coordination and reported research evidence; it does not establish that combining
our implementations would improve ROSA.

## What was accessed and how far this review goes

Authenticated GitHub reads enumerated all three current branch tips:

| Branch | Pinned commit | Published files |
|---|---|---:|
| `main` | `26ac7bd9bd65abeb5ff672c045f209e602a0af9e` | 8 shared files |
| `member/krln` | Same commit as main | Same 8 files; no member research snapshot yet |
| `member/levinson` | `e12d88b9ecbe2f72869f16b4f79cd568cd74576e` | 100 files, including the same 8 shared files |

All **100 unique tracked files**, totaling **1,069,099 source bytes**, were
downloaded into [snapshot/](snapshot/). Every downloaded byte sequence matched
its Git blob hash. All **91** allowlisted research files also matched the
manifest's `published_sha256`. The member manifest accounts for the remaining
file. The repository has **12 published study bundles**, plus navigation,
decisions, literature pointers and historical summaries.

Reading depth was not uniform. The shared protocol, onboarding, helper code,
tests, manifest, current state, study index, scorer decision and latest comparison
reports received detailed review. Older studies, long design investigations,
protocols and supplementary tables received section/decision/limitations review,
with targeted reading of relevant details. The retained
[reading map](remaining-reading-map.json) explicitly labels its section excerpts.
This is a broad contextual review of the published repository, **not a claim
that every historical paragraph or code path received an exhaustive audit**.
Full downloaded files are retained for deeper follow-up; coverage is not inferred
merely from having downloaded a file.

The snapshot's synchronization time is **2026-11-15T16:57:29Z**, which is
**2026-11-16 00:57:29** on the owner's local clock. Its documents include some
November 16 amendments despite older snapshot headings. Use dated source text
and manifest hashes rather than treating every header as equally current.

This review does not include every Git history revision, raw experimental
archive or external source repository linked from these documents. Repository
instructions were read as third-party context. They did not authorize execution,
supersede Martin's decisions, or become local agent instructions automatically.

## What the repository actually implements

The [shared README](snapshot/README.md) and [protocol](snapshot/PROTOCOL.md)
describe one-way, curated context mirrors. A member's original local research
remains authoritative. `main` carries shared tools/rules; a member publishes their
own `member/<name>` branch. Protocol updates require an ordinary merge into the
member branch rather than appearing automatically.

`scripts/context_sync.py` reads an explicit include list. It checks source and
target repository/branch identity, detects unexpected remote advances, checks
local managed-file edits, scans text, redacts selected local paths/private IPv4
addresses, records provenance and hashes, and requires confirmation for managed
deletions. Preview does not write context files. Sync makes local copies and
updates its manifest; it does not stage, commit or push. Publication is a separate
reviewed Git action.

This is useful shared project context, not a runtime robot skill, verified
episodic memory, benchmark database, full backup or proof of research novelty.
Receiving this URL does not require installing a package, replacing our agent
loop or reorganizing our local project.

## What Levinson is currently investigating

The [active state](snapshot/research/ACTIVE_STATE.md) describes a training-free
ROSA tool-calling improvement, retaining model judgment for semantic decisions.
The owner selected the fixed tool loop as the working base. The final paper
claim, precise method freeze and wider evaluation remain open. December 2 is
reported as the presentation date, not a confirmed paper submission deadline.
Those are Levinson's project decisions, not newly imposed requirements for ours.

His read-only fixed loop C1 is still model-directed execution through LangChain
and ROSA tools. It restricts the offered read menu, returns recoverable errors
for model correction, validates supported argument-schema features and provides
a final-answer interface. The latest work tests an answer gate and list-valued
arguments. This should not be reduced to one isolated new tool-selector algorithm.
The implementation details here are reported in source-review documents; the
research Python implementation itself is deliberately absent from this mirror.

### Matched development comparison

I independently summed the **80 published same-cell table rows**, reproducing:

| Configuration | Supported completions | Requests |
|---|---:|---:|
| C1 fixed loop, historical control | 70/80 | 486 |
| Released Forge comparison | 55/80 | 643 |
| A1 stock executor with altered/deconflicted prompt | 47/80 | 472 |

These are four local models, ten development tasks and two seeds. Qwen contributes
20/20 C1, 18/20 Forge and 19/20 A1. A1 is not unmodified-prompt stock ROSA; its
larger tool menu is a real difference. C1 and A1 are historical controls, not
concurrent reruns. The reports retain changing-fixture missed-trigger defects
and two Forge requests with unknown token usage. Thus these totals support a
reported development comparison, not a universal ranking or causal claim.

The independently checked arithmetic is a **table recount**, not independent
trace verification. The separate check recorded by Levinson's own reviewer is
still reported evidence from our perspective: its raw inputs are not in this repo.

### Latest build round: the important qualification

The 320-episode build report uses a **fresh** fixed-loop control:

| Configuration | Supported / 80 | Requests | Reported total tokens |
|---|---:|---:|---:|
| Fresh fixed loop | 67 | 506 | 1,995,814 |
| Plus answer gate | 70 | 541 | 2,791,741 |
| Plus list arguments | 67 | 435 | 1,524,630 |
| Both add-ons | 69 | 468 | 1,630,657 |

I reproduced these sums from the published per-model table. The historical
70/80 control and fresh 67/80 control must not be interchanged.

The report explicitly declines mechanism attribution: the four cells won by the
gate had no gate firing, and three had control-side defects. The list arm used
lists in only 4/80 episodes; its aggregate savings arose in episodes without a
list call. Reported changes may involve schema/prompt effects and run variability.
This is a useful negative/inconclusive attribution result, not demonstrated
success of either add-on. Frozen criteria were met literally; that alone did not
identify the cause of the apparent gain.

### Research history worth retaining

| Published study area | Reported lesson and scope |
|---|---|
| Capability discovery | Matching values and shapes do not establish semantic interchangeability. Five false supports among seven initially supported extension pairs; substitution was never authorized. |
| CPAW | Bounded synthetic certificate/batching prototype; no consistent advantage over strong exact controls and 0/47 default-registry eligibility under its strict contract. No general impossibility claim. |
| Native-read execution | Ordinary concurrency/persistent transport can help local execution; the inspected historical opportunity was small relative to inference time. No adaptive algorithm promoted. |
| Action narration | Terse instructions saved generation on a selected supported subset but lost evidence coverage elsewhere; larger cases had context/truncation and closeout limitations. |
| GPT coverage | Complete factual field coverage and compliance with required operation order were distinct; the report records 92/92 fields but only 7/10 strict completions. |
| AutoTool continuation | Offline replay and adversarial revisions found no complete read-action matches over 269 continuation boundaries and no useful incremental contrast over the stated ordinary control; live gate remained blocked. |
| Headroom diagnostics | Prompt contradictions and discovery-first instructions explained part of avoidable work. Stronger prompting did not universally fix Qwen: the later A2 condition lost supported completion, 20/24 versus 24/24. |
| Residual failures and waste | Scoring conventions, wrong entity/source selection, loops, unnecessary reads and output rendering were separate causes. Revised attribution rules agreed on only 6/10 hand-checked labels; fine-grained percentages remain uncertain. |
| Earlier design and R5–R28 history | Many conditional wins disappeared against strong ordinary controls; missing original evidence and unmirrored archives are disclosed. Proposed helpers, graphs and prior-art comparisons are not all implemented systems. |

These are member-reported findings. I did not rerun the studies or independently
check the primary literature cited in historical investigations during this review.

## Where I agree with ChatGPT, and what needs qualification

1. **Coordination is the correct role.** Keep the two research implementations
   separate. The repo can prevent duplicated work and expose relevant negative
   findings without being inserted into a ROSA runtime.
2. **The comparison is more than code quality.** Shorter menus, error handling,
   terminal schemas, prompts, model settings and fixtures all matter. The counts
   cannot isolate the fixed loop as the sole cause of an improvement.
3. **Qwen's success there is relevant but not parity evidence.** These are
   read-only graph/parameter queries, not our UR5e movement/clarification suite.
   The latest local setup reports temperature 0.7, 65,536 context, 4,096 output,
   up to 40 iterations and a 900-second episode limit. Our M4 profile used
   temperature 0, 8,192 context, 1,024 output/call, eight calls and 360 seconds.
   This does not justify copying a 64K context setting onto our 6 GB GPU or
   replacing our frozen failure scores with his 20/20 result.
4. **Source review is constrained here.** We can inspect the synchronization
   implementation and its ten defined tests. We cannot conduct the same direct
   runtime-source review of C1, the research scorer or new add-ons from this
   context-only mirror. Their linked Python sources, original freezes, raw traces
   and some recent reports are excluded. Claims that integration will work or
   improve performance remain hypotheses.
5. **The sync-code concerns are plausible, with appropriate scope.** The code
   checks final-component symlinks but does not visibly establish containment of
   every intermediate source/target/manifest directory. Individual `os.replace`
   calls are atomic; the whole multi-file write/deletion set has no rollback
   transaction. Regex scanning does not guarantee confidentiality. These are
   static hardening findings, not demonstrated exploitation or data loss.
   I counted ten test definitions but did not execute the helper or test suite.
   No CI workflow is present in the inspected trees.

## Provenance and missing context

The manifest records **90 ignored source files and one modified-or-staged file**
(`ACTIVE_STATE.md`). All 91 have `source_commit_contains_bytes=false`.
The listed source commit therefore does not reproduce the published text, even
though the snapshot itself is committed and its published hashes verify.
Source hashes cannot be independently checked without access to the corresponding
unredacted source bytes; only published hashes were checked here.

Explicit exclusions include raw traces, research Python, runtime dependencies,
private configuration/maps, archives, held-out requests/answers/routes and Claude
Project documents. Some newer studies named by ACTIVE_STATE and some older
reports are absent. Missing relative links are expected, but they cap verification.
The original 64 structured-dependency traces and Mission C report are reported
unavailable; a reconstruction must not be treated as the originals.

The F/R/P labels inside teammate documents are relative to their author's
inspection, not a claim that I reproduced those results. The manifest timestamp
is snapshot provenance, not proof of the teammate's live process state today.

## Fit with our project and recommended use

Our bounded macros replace routine execution after the model chooses an
application-authorized skill, with independently scored outcomes. Levinson's
current fixed loop leaves more of the tool sequence with the model and aims for
broader tool-loop improvements. Both can encounter wrong semantic choices and
truthful reports for the wrong goal. Returning an error, verifying observations
and satisfying the user's request remain different properties.

There is coordination overlap around deconflicted prompts, strong batching
controls, error feedback, reporting contracts, cost accounting and negative
findings. A future combined implementation is conceptually possible, but would
need checked interfaces, shared cost accounting, permissions, cancellation,
evidence freshness and terminal semantics. That work is not performed or
authorized by this review. Existing success rates and request counts cannot be
pooled across these studies.

Use the published snapshots as a read-only reference before a substantial new
research proposal, check the latest branch/manifest then, and clearly label
intentional replication or overlap. No automatic syncing or future background
monitoring was configured. Publishing Martin's context requires a separately
reviewed allowlist and authorization; the current master includes machine paths
and links to private local evidence and should not be uploaded wholesale. Also,
our current master is in `rosa-evaluation`, whereas this sample manifest mirrors
`rosa-research`: one-source relative paths and authority must be decided explicitly.

**Our immediate state is unchanged:** G1 Stage 3 cannot freeze because of the
substantive clarification-scorer finding, unmet full error-observability scope
and missing uninvolved human clarification ratings. Teammate findings do not
clear those gates, authorize new source changes or launch another experiment.

## Local evidence and changes

- [Branch inventory](BRANCH_REVIEW.json), [100-file verification](SNAPSHOT_VERIFICATION.json),
  [offline checks](READ_ONLY_CHECKS.json), [reproduction script](verify_snapshot.py).
- [Downloaded source bundle](downloaded-snapshot.json), exact extracted files in
  [snapshot/](snapshot/), section-reading map linked above.
- This report and the living master link are local documentation. No teammate
  branch was modified, no sync was run, and no Git commit, push, upload, OAuth,
  model experiment or robot action was performed.
