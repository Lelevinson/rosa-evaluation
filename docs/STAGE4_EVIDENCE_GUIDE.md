# Reviewing the Stage 4 evidence

Start with the final report in
`artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md`.
It distinguishes the original JTVR policy study, the preserved Baseline v1,
the interrupted movement V2 work, and the new live reliability/batching study.
The six-stage roadmap is `PROJECT_ROADMAP_SIX_STAGES.md`.

## Offline checks: no sign-in or new inference

The final ZIP and its SHA-256 file are in `artifacts/`, named
`ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.zip` and the same stem with `.sha256`.
In Windows PowerShell, from the evaluation checkout:

```powershell
Get-FileHash -Algorithm SHA256 .\artifacts\ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.zip
Get-Content .\artifacts\ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.sha256
```

In WSL, from the evaluation checkout, Python 3.12's standard library is enough:

```bash
python3 -B -m zipfile -t artifacts/ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.zip
python3 -B -m experiments.stage4_batching.offline_review
```

The review command checks all archived source hashes and the job manifest,
replays the recorded state audit for all 160 trials, recomputes summaries from
exported Phoenix spans, and checks them against the saved audit records. It
does not contact Phoenix, ROS, Ollama or the hosted backend, and writes no files.
It reuses the study's audit functions; it is a consistency check, not a newly
authored evaluator or an independent replication. It exits nonzero on mismatch.

The frozen audit passed 152/160 records and failed eight recovery-stop traces.
The supervisor's original `FAILED` status is preserved. A separate
`audit-reconciliation.json` accounts for the eight missing final tool spans by
checking raw model requests, callback counts, world calls and attributed guard
reports. The offline command replays those narrow checks and returns
`PASSED_WITH_DOCUMENTED_TRACE_GAPS`; it does **not** claim complete tool-span
coverage. `trace_complete` describes closure of exported spans and cannot detect
a span that was never completed/exported. Task scores and trials are unchanged.

The ZIP's `evidence-manifest.json` records SHA-256 for every curated member other
than the manifest itself. ZIP packaging verifies every member against those
hashes as well as checking CRCs. The manifest's paths start at the evaluation
repository root; they also identify files inside the ZIP.

## Reading the raw data

- `analysis.json`: aggregate metrics, matched pairs, retention decisions and limits.
- `all-trials.csv`: all attempts, including failed tasks and operational exits.
- `siwc/result.json` and `ollama/result.json`: complete backend schedules and settings.
- Each `trials/RUN_ID/`: raw result, state/evidence record and exported trace.
- `audit.json`: state checks and Phoenix accounting for each trial.
- `audit-reconciliation.json`: post-run accounting of the eight explicit trace gaps.
- `ros/`: resets, independent evaluator queries and instrumented server records.
- `freeze.json`, `jobs.json`, `source/`: byte-exact execution inputs and identities.
- `analysis-source/`: later analysis/review code, kept outside the execution freeze.
- Preflight directories and dispositions: infrastructure failures and accepted controls.
- `resource-samples.csv`: sampled host free memory, not process memory peaks.
- `preservation.json`: historical archive hashes and repository base identities.

An audit pass means the records agree; task success is a different field.
Read strict compliance, physical outcome and operational completion separately.
`api_failed` includes agent iteration-limit exits and does not mean every such
trial suffered an HTTP failure. Raw tool arguments precede schema coercion.
The `error_type` field records exceptions reaching the outer runner. ROSA can
return an internal validation failure as an error string with `error_type=null`;
the operational flag and saved answer still record that failure.

## Reconstructing execution

Live execution used ROS 2 Jazzy on WSL Ubuntu 24.04 and separate locked uv
environments for research and Phoenix. The freeze records Python/dependency
versions; the source snapshot includes both evaluation and modified research
checkouts. The research base commit alone does not include those local changes.

Restore the frozen files from `source/` into a **new** sibling-checkout workspace
before exact hash verification. Git line-ending conversion can change working
bytes, so use the archived copies. Restore historical context from the preserved
archives if running the protocol's historical-source checks. Adapt local paths,
create the locked environments from the archived manifests, source ROS Jazzy,
and start the separate Phoenix service. The campaign logs record the live runner
and audit module commands; the audit uses Phoenix's environment.

Do not launch into this existing campaign. The runner refuses to overwrite it.
A new live replication needs a separately named campaign/project, a newly frozen
protocol and fresh hosted consent with its declared request budget. Keep new
results separate rather than overwriting failed trials. Offline review needs none
of that live setup. The evidence archive can be examined without rerunning models.
