# Llama and Granite: completed integration investigation

Date: **2026-11-17**. This is a separate post-hoc engineering investigation, not a robotics performance benchmark or a rerun of M4/G1.

## Findings

**The initial zero-completion results do not establish that Llama or Granite are inherently incompatible with ROSA. We found concrete template/interface problems, and both models returned correct native report calls in a small combined-configuration test.** This is readiness evidence for further validation, not proof that the full robotic tasks are now fixed.

1. **Llama's saved template does not keep tool schemas in its follow-up branch.** The function-definition block is inside the condition that the current message is both a user message and the last message. When the history ends with a tool result, that branch is skipped. Our earlier claim that schema fields were model-visible because they appeared in the API request was too strong: the JSON request and the rendered model prompt are different layers. We inspected the saved template and requests; we did not capture the server's fully rendered tokenizer prompt. The structural issue is clear, but its precise contribution to historical failures has not been isolated.
2. **Granite's custom system prompt bypasses its default native-call formatting guidance.** The saved template includes that guidance only when there is no custom system message. ROSA supplies one. In the new harmless probe, adding the template's own native syntax guidance produced the exact expected call in 4/4 configurations (raw/adapter crossed with streaming on/off). Generic custom instructions produced 0/4; no-custom-system produced 0/4 exact calls because the returned arguments were nested incorrectly. Thus removing the custom system alone did not fix it. These four configurations repeat one tiny request, not four independent task families.
3. **The existing Python adapter did not drop native calls.** Call names/counts matched the captured server responses throughout all 48 requests. However, it normalized two Llama stringified `nodes` lists into actual arrays. Those two successful argument checks are combined-system successes, not exact schema compliance at the server response boundary. The server response itself is already parsed by Ollama; it is not a raw model-token dump.
4. **The intended streaming setting was not the effective HTTP setting.** In the pinned `langchain-ollama` 0.3.10, `streaming` is not a recognized model field and extra constructor fields are ignored. A zero-network mock reproduced `stream=true` from the existing `streaming=False` constructor. Explicit invocation `stream=False` produced `stream=false`. The frozen ROSA call path does not explicitly supply that override. Earlier reports' “streaming off” wording should therefore be read as application/output streaming disabled, not verified nonstreaming HTTP transport. Earlier per-call HTTP bodies were not retained, so this finding is a reproduced configuration-path result rather than a retrospective wire capture of every benchmark call. Streaming toggles did not change exact-call correctness in the basic probes here.
5. **Tool-result names are omitted by the pinned message converter.** A small opt-in test preserved `tool_name`, but it did not improve the paired SUCCESS fixture: Llama failed both versions and Granite passed both. This is an interoperability concern, not an established explanation for the previous zero scores.

## Bounded live results

All 48 scheduled local requests were made once. No retries, hosted requests, actual tool execution, robot command, Gazebo launch, model/template installation change, or alteration of old scores occurred. There were two Qwen positive controls, 23 Llama probes and 23 Granite probes. Settings were context 8,192, output at most 512/call, temperature 0 and seed 42. GPU idle preflight passed. Models were unloaded afterwards. The original 69 frozen source/config hashes and model digests remain unchanged.

| Check | Llama | Granite |
|---|---:|---:|
| Basic native probe, no custom system (two channels × two stream settings) | 4/4 | 0/4 exact; malformed native arguments |
| Basic native probe, generic custom system | 4/4 | 0/4; no native calls |
| Basic native probe, generic plus native formatting guidance | 4/4 | 4/4 |
| Synthetic SUCCESS/UNKNOWN after a tool result, generic system | 0/2 | 2/2 |
| Same two follow-ups, persistent schemas alone | 0/2 | 0/2 |
| Same two follow-ups, native formatting plus persistent schemas | 2/2 | 2/2 |
| Synthetic read call, generic/persistent-schema variants | 2/2 after normalization; 0/2 exact raw server arguments | 0/2 |
| Correction after malformed report, generic/persistent-schema variants | 0/2 | 0/2 |
| SUCCESS follow-up preserving tool_name | 0/1, same as baseline | 1/1, same as baseline |

The combined variant passed one SUCCESS and one UNKNOWN fixture for each model. Native guidance alone was not separately tested on those follow-up fixtures, so this does not isolate the independent benefit of schema persistence. Schema persistence alone sometimes made behavior worse. Correcting a malformed prior report still failed in the tested variants. We cannot claim a general solution, restored recovery, or a new robotics completion rate.

The Qwen raw and adapter positive controls both returned the requested call. Raw-versus-adapter probe request bodies differed only by the SDK omitting empty `images` arrays; they were not byte-identical. Every actual body difference is retained in the evidence.

## Instrumentation exception and offline reconciliation

My diagnostic used an overly strict equality assertion between a manually constructed SDK request and the SDK's actual outgoing request. It ran **after** the model response returned. The SDK removes empty fields and auxiliary message/call metadata, so 35 adapter records were initially labeled assertion errors. All actual requests and complete response objects had already been captured. Those original errors remain in the unchanged raw archive.

I replayed each of those 35 captured responses through the same frozen adapter with `httpx.MockTransport`. Every replay asserted that its outgoing JSON exactly matched the captured live request. This used **zero additional network/model requests** and recovered the adapter's parsing of the already-observed response. The reconciled records remain separate from the original error records. No failed model outcome was resampled or silently replaced. Assertions and known normalization are documented rather than hidden.

The early flag `all_server_native_calls_preserved` in the reconciled data is a strict argument-equality check and is false for the two list normalizations. The independent verification distinguishes preserved call names/counts from altered argument representation; it does not interpret that flag as dropped calls.

## What this changes about the old interpretation

Llama's historical native calls and sometimes successful physical movement were real, but its reporting failures cannot be confidently attributed solely to the model ignoring schemas that it demonstrably saw. Request-level visibility did not establish follow-up prompt visibility. Granite's zero native operations reflected the tested integration arrangement, not a proof of universal lack of tool-calling capability. The native-guidance probe gives a concrete counterexample to such an absolute claim.

The old 80-trial scores remain valid records of those exact combined systems. They are weak evidence for ranking intrinsic model robotics ability. The earlier failure to gate readiness before the full Granite campaign remains a procedural limitation. The earlier report and evidence ZIPs are preserved unchanged; this dated report supersedes overbroad compatibility and streaming interpretations.

## Recommended minimal next step

Build an **opt-in integration profile** that keeps the actual supplied schemas available across tool-result turns, preserves documented native calling guidance alongside ROSA's task instructions, and explicitly sets the intended HTTP streaming option. Keep validation, permissions, evidence verification, error budgets and model decisions unchanged. Do not accept `classification` as an automatic alias for `status`, or execute JSON/code prose to improve scores. If retaining tool names, label and test that change separately because this probe did not establish a benefit. Persistent schemas and guidance consume extra input tokens; having no additional model turn does not make the change free. This small investigation does not establish an end-to-end efficiency benefit.

The diagnostic already contains isolated prototypes of these prompt/message variants; they have not been deployed into the frozen ROSA runtime. Validate the chosen profile on fresh short complete-loop fixtures, including valid reports, UNKNOWN, failed execution and correction after feedback, before another robot benchmark. All tested backends should receive the same semantic contract and equivalent budgets; any backend-native formatting differences must be documented. The combined 2/2 toy result is not enough to skip that validation.

No G1 gate was cleared and no new held-out stage or 80-trial rerun was launched.

## Evidence

The archive contains original source/protocol, model templates, installed adapter inspection, live HTTP bodies/responses, original assertion failures, exact-request offline replays, source freeze and manifests. No headers or credentials were recorded. Independent local verification checked every outer and nested original archive hash, original source snapshot hashes, model digests, the 48-job schedule and request accounting. No Phoenix server-side audit was run for these HTTP-level diagnostics; they are not presented as the earlier audited robotics pipeline.

Official references: [Ollama tool-calling request and tool-result format](https://docs.ollama.com/capabilities/tool-calling), [Granite 3.3 capabilities](https://ollama.com/library/granite3.3). The exact installed saved templates and source take precedence over current online defaults.

## Request-level results

| Request | Model | Exact expected call at server boundary | Exact expected call after adapter |
|---|---|---:|---:|
| 01-positive-control-raw | qwen3.5:9b | True | True |
| 02-positive-control-adapter | qwen3.5:9b | True | True |
| 03-probe-none-stream0-raw | llama3.1:8b-instruct-q4_K_M | True | True |
| 04-probe-none-stream0-adapter | llama3.1:8b-instruct-q4_K_M | True | True |
| 05-probe-none-stream1-raw | llama3.1:8b-instruct-q4_K_M | True | True |
| 06-probe-none-stream1-adapter | llama3.1:8b-instruct-q4_K_M | True | True |
| 07-probe-generic-stream0-raw | llama3.1:8b-instruct-q4_K_M | True | True |
| 08-probe-generic-stream0-adapter | llama3.1:8b-instruct-q4_K_M | True | True |
| 09-probe-generic-stream1-raw | llama3.1:8b-instruct-q4_K_M | True | True |
| 10-probe-generic-stream1-adapter | llama3.1:8b-instruct-q4_K_M | True | True |
| 11-probe-native-stream0-raw | llama3.1:8b-instruct-q4_K_M | True | True |
| 12-probe-native-stream0-adapter | llama3.1:8b-instruct-q4_K_M | True | True |
| 13-probe-native-stream1-raw | llama3.1:8b-instruct-q4_K_M | True | True |
| 14-probe-native-stream1-adapter | llama3.1:8b-instruct-q4_K_M | True | True |
| 15-report-SUCCESS-schemas0-adapter | llama3.1:8b-instruct-q4_K_M | False | False |
| 16-report-SUCCESS-schemas1-adapter | llama3.1:8b-instruct-q4_K_M | False | False |
| 17-report-UNKNOWN-schemas0-adapter | llama3.1:8b-instruct-q4_K_M | False | False |
| 18-report-UNKNOWN-schemas1-adapter | llama3.1:8b-instruct-q4_K_M | False | False |
| 19-read-SUCCESS-schemas0-adapter | llama3.1:8b-instruct-q4_K_M | False | True |
| 20-read-SUCCESS-schemas1-adapter | llama3.1:8b-instruct-q4_K_M | False | True |
| 21-feedback-schemas0-adapter | llama3.1:8b-instruct-q4_K_M | False | False |
| 22-feedback-schemas1-adapter | llama3.1:8b-instruct-q4_K_M | False | False |
| 23-report-SUCCESS-toolname-adapter | llama3.1:8b-instruct-q4_K_M | False | False |
| 24-combined-SUCCESS-adapter | llama3.1:8b-instruct-q4_K_M | True | True |
| 25-combined-UNKNOWN-adapter | llama3.1:8b-instruct-q4_K_M | True | True |
| 26-probe-none-stream0-raw | granite3.3:8b | False | False |
| 27-probe-none-stream0-adapter | granite3.3:8b | False | False |
| 28-probe-none-stream1-raw | granite3.3:8b | False | False |
| 29-probe-none-stream1-adapter | granite3.3:8b | False | False |
| 30-probe-generic-stream0-raw | granite3.3:8b | False | False |
| 31-probe-generic-stream0-adapter | granite3.3:8b | False | False |
| 32-probe-generic-stream1-raw | granite3.3:8b | False | False |
| 33-probe-generic-stream1-adapter | granite3.3:8b | False | False |
| 34-probe-native-stream0-raw | granite3.3:8b | True | True |
| 35-probe-native-stream0-adapter | granite3.3:8b | True | True |
| 36-probe-native-stream1-raw | granite3.3:8b | True | True |
| 37-probe-native-stream1-adapter | granite3.3:8b | True | True |
| 38-report-SUCCESS-schemas0-adapter | granite3.3:8b | True | True |
| 39-report-SUCCESS-schemas1-adapter | granite3.3:8b | False | False |
| 40-report-UNKNOWN-schemas0-adapter | granite3.3:8b | True | True |
| 41-report-UNKNOWN-schemas1-adapter | granite3.3:8b | False | False |
| 42-read-SUCCESS-schemas0-adapter | granite3.3:8b | False | False |
| 43-read-SUCCESS-schemas1-adapter | granite3.3:8b | False | False |
| 44-feedback-schemas0-adapter | granite3.3:8b | False | False |
| 45-feedback-schemas1-adapter | granite3.3:8b | False | False |
| 46-report-SUCCESS-toolname-adapter | granite3.3:8b | True | True |
| 47-combined-SUCCESS-adapter | granite3.3:8b | True | True |
| 48-combined-UNKNOWN-adapter | granite3.3:8b | True | True |

Input tokens: **11,027**. Output tokens: **1,319**. Verified outer content files: **67**; nested original content files: **61**.

Evidence SHA-256: `68ab14ca7a8fd7dc9c9e2ecdf28987d1a950057e0c81abe48b32380a3be1fddb`.
