# Phase 4 v2

The root workspace `PHASE4_V2_PLAN.md` defines the fixed experiment and acceptance
criteria. Old `experiments/stateful/`, its benchmark, archived sources and results
remain unchanged. This package adds contract checks and new experiments.

In the prepared WSL research environment, from the evaluation repository:

```bash
.venv/bin/python -B -m experiments.phase4.campaign prepare
.venv/bin/python -B -m experiments.phase4.campaign launch
```

The first command validates, records a source/manifest freeze, runs the scripted
controls and audits, and diagnoses local inference. The second launches a durable
supervisor: hosted consent/batch, hosted audit, local batch, local audit, cleanup
and report. It will need one fresh browser consent. Existing incomplete/failed
steps require review and are never silently rerun or overwritten.

Progress and artifacts live in `../reports/phase4-v2/`. Individual run artifacts
and live Phoenix traces use the existing results store. The final archive
excludes actively changing supervisor/campaign/report-log files and includes a
stable execution checkpoint with exact completed command records.

Use `retrospective` alone to inspect additional v1 contract metrics; this does
not rerun or rewrite v1 scores. The final v2 report distinguishes orchestrator
repairs, strict compliance and physical goals. All observed failures remain.
