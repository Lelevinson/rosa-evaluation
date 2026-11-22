# Weekend 2026-11-21/22 — final summary (session A, laptop D16/PX-1)

All runs: laptop RTX 4050 6 GB (Qwen 17/33 layers on GPU, others per load checks), G1 digests and settings, own Ollama 0.40.6 on port 11440, no machine mixing, timing descriptive only. Chain ended 2026-11-22 01:08 TPE ("CHAIN END"); no trial jobs, no chain, no gazebo process remain. Idle services still up: Ollama (our port 11440) and owned Phoenix tmux (port 6006). Free disk C: ~20 GB. Chain gates: `weekend-run-20261121/gates/*.json`.

## Finished
| Item | Result |
|---|---|
| F1 Qwen wording, held-out (Qwen + Sol, 60 trials each) | Verdict **NOT ADOPTED** (net 0 on known-goal; no censoring; no P-f′ veto). Qwen inspection-first 4 → 0 is diagnostic only. |
| Parity Phase B acceptance | Qwen PASS, Ministral PASS (reference). **Llama PASS** (native-schema-v1, adapted). **Granite FAIL**: arguments double-wrapped; fix would need argument repair, not allowed. Not admitted. |
| SDK list-string → array normalization | Assistance, reported separately (Llama: 14 of 86 raw calls). |
| Gazebo D1 | Controls 52/52, dev 48/48, PASS. |
| Gazebo D2 held-out | 160/160 trials, no crashes, no censoring. Known-goal passes /18 (primitives / macro): Sol 18/18, Qwen 12/13, Ministral 16/15, Llama 8/11. Fewer calls in macro for all four (33–48%). Macro not worse on passes for all four. "Native operations not lower in macro": against for Qwen only. Qwen failures: 10 of 11 inspection-first (PRELIMINARY). |
| Phase C Llama (adapted-integration rerun, laptop), 76 G1 held-out cases | 43 PASS / 33 FAIL, 0 censored, 0 pending. By arm: primitives 23/38, macro 20/38. 4 semantic judgments pending (cases 033 and 052, both arms). `final_campaign_verdict: WITHHELD_PENDING_REVIEW_OR_RESULTS`. Not a replacement for the lab G1 result. |

## Preliminary until humans rate
Ambiguous cases: F1 24, Phase C 4, D2 16. Blinded kits (labels hidden, no ratings, no AI ratings):
- F1: `artifacts/f1-catalogue-wording-20261121/review-kit-stage1b/` (branch member/martin-f1)
- Phase C: `artifacts/parity-integration-20261121/phase-c-review-kit/` (member/martin-parity-runs)
- D2: `artifacts/gazebo-d-20261121/d2-review-kit/` (member/martin-gazebo-runs)

Send `packet/` only to Levinson. Private keys are kept off git (local + backup folder); each kit has `KEY_SHA256.txt` so the key can be verified later without revealing it. Generator: `tools/review_kits/build_kit.py`.

**Incident (2026-11-22):** the first versions of the three kits had their `private-key.json` pushed to public branches (still in git history). Nothing had been sent or rated, so all three kits were regenerated with fresh random labels; the leaked keys no longer match. The old G1 `packet-map.json` is also public but already rated, so no effect.

## Not done / designed only
- Granite adapter iteration (no admissible fix under parity rules).
- Human ratings, lab G1 comparison (needs lab).

## Incidents (no effect on results)
- CUDA load failure until a full Windows restart. Pulls dropped over VPN, retried.
- WSL git false "dirty" (fileMode/CRLF) stopped F1 dev r0 and Phase C Llama before any trial; fixed with `git -c core.fileMode=false -c core.autocrlf=true`; the Phase C run folder was reused (0 trials had run).
- Known frozen-input doc drift: macro-m5 status.json (pre-freeze commit 37a7e19), recorded.
- Page file / hibernation file were removed on Windows during the weekend; I assumed the owner did this.

verify_freeze output: see below, per branch.
