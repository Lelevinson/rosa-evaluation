# M5 delivery and retrospective postprocessing

These utilities are separate from frozen experiment policies. They never add
observations to M4 or alter its scores, prompts, thresholds or runtime sources.

The runtime uses the existing research/Phoenix uv locks and Python3.12 in WSL.
The report/video operator used existing Windows Python3.14 packages and FFmpeg;
`requirements-recorded.txt` and the artifact toolchain record capture versions.
No report dependency was installed into or used to replace the research environment.
This records the tested laptop workflow, not a fresh-OS installation certificate.

From the evaluation checkout, after restoring M4 and M5 artifacts:

```powershell
python -B -m tools.m5.analysis
python -B -m tools.m5.report
python -B -m tools.project_context --refresh --check
```

The first command regenerates only M5 tables/exploratory summaries. The second
regenerates the ten-page report, ledger and figures from saved data. Both are
post-hoc; they do not change M4's predefined screen. Report dependencies are
recorded, while the video's Arial path and FFmpeg executable are Windows-specific.

`evidence.py` creates the single-use review packet and trace extraction. Its
packet creation refuses to replace an existing packet, preserving reviewer context.
For forensic extraction alone, import and call `forensic()`; do not regenerate
ratings or overwrite future human responses. The original packet contains no
model/condition labels or operator ratings; keep the operator key separate.

`package_validation.py` runs in the existing WSL research environment and builds
offline/installs into an empty target. It refuses populated output paths. The
initial incorrect probe is retained as `package-attempt-01`; final `package/`
passed after using the public snapshot API, with no runtime change.

`demo_capture.py` is **live presentation execution**, not passive postprocessing.
It starts an isolated camera world and makes up to eight requests per explicitly
selected backend. Do not invoke it casually to reproduce a report, repeat failed
takes for a favorable result, or use physical hardware. The two accepted M5 runs
made four requests total and are separate from all M4 measurements. A zero-model
camera preflight was completed first. `video.py` edits those original camera
frames, labels accelerated waiting and preserves actual motion; it refuses to
replace an existing MP4. Camera rendering can affect timing, so the demo is not a
new backend-speed benchmark.

`backup.py`, `backup_lockfiles.py` and `remote_verify.py` are operator backup
utilities. Creating a local backup does not authorize publication or prove it is
off-machine. The initial broad lock filter omitted14 retained uv.lock copies;
the addendum preserves them and the filter is corrected. Two exact-file expired
OAuth sentinel findings were reviewed; genuine token patterns are not generically
suppressed. Protected credential storage, service databases and environments are
excluded. No new consent is auto-approved, and private records are never logged.

The public evaluation push was rejected by automatic approval review pending
explicit authorization to disclose the retained source/evidence payload. Do not
bypass that rejection through another public transfer. Use only a user-approved
destination. `remote_verify.py` reads backups; it does not upload them.
