"""Independent evidence verification and descriptive integration report."""
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import zipfile

BASE = Path(__file__).resolve().parents[1]
EVAL = Path(__file__).resolve().parents[3]
EVIDENCE = BASE / 'evidence'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify_archive(archive):
    assert archive.testzip() is None
    manifest = json.loads(archive.read('ARCHIVE_MANIFEST.json'))['files']
    for name, expected in manifest.items():
        assert sha(archive.read(name)) == expected, name
    return len(manifest)


def main():
    path = EVIDENCE / 'INTEGRATION_RECONCILED_EVIDENCE_2026-11-17.zip'
    with zipfile.ZipFile(path) as z:
        file_count = verify_archive(z)
        with zipfile.ZipFile(io.BytesIO(z.read('LAB_INTEGRATION_DIAGNOSTICS_2026-11-17.zip'))) as original:
            original_files = verify_archive(original)
        data = json.loads(z.read('RECONCILED_RESULTS.json'))
        initial = json.loads(z.read('status.json'))
        freeze = json.loads(z.read('freeze.json'))
        zero = json.loads(z.read('zero-network-results.json'))
        for name, expected in freeze['files'].items():
            assert sha(z.read(name)) == expected
        old_path = EVAL / 'artifacts/lab-multimodel-20261117/evidence/ROSA_LAB_MULTIMODEL_2026-11-17.zip'
        with zipfile.ZipFile(old_path) as old:
            old_freeze = json.loads(old.read('study/freeze.json'))
            for name, expected in old_freeze['files'].items():
                assert sha(old.read(name)) == expected
            assert sha(old.read('study/freeze.json')) == freeze['original_freeze_sha256']
            assert all(old_freeze['model_metadata'][m]['digest'] == d for m,d in freeze['model_digests'].items())
        assert initial['reserved_requests'] == data['actual_live_requests'] == len(data['results']) == 48
        assert [r['job'] for r in data['results']] == freeze['schedule']
        assert data['additional_live_requests'] == data['tool_executions'] == 0
        assert data['offline_mock_replays'] == data['original_instrumentation_assertion_failures'] == 35
        calls_preserved = all([c['name'] for c in r['server_native_calls']] ==
            [c['name'] for c in r['parsed_calls']] for r in data['results'])
        assert calls_preserved
        for row in data['results']:
            options = row['actual_wire_request']['options']
            assert options['num_ctx'] == 8192 and options['num_predict'] == 512
            assert options['temperature'] == 0 and options['seed'] == 42
            assert row['actual_wire_request']['stream'] == row['job']['stream']
        normalizations = [{'id':r['job']['id'],'raw_server':r['server_native_calls'],
            'after_adapter':r['parsed_calls']} for r in data['results'] if not r['parser_preserved_server_calls']]
        assert len(normalizations) == 2
        for item in normalizations:
            assert isinstance(item['raw_server'][0]['args']['nodes'], str)
            assert item['after_adapter'][0]['args']['nodes'] == ['/lab_stub']
        paired = json.loads(z.read('RAW_ADAPTER_PAIR_DIFFERENCES.json'))
        assert len(paired) == 12
        for pair in paired:
            assert all(d['path'].endswith('/images') and d['expected'] == [] and d['actual'] is None
                for d in pair['body_differences'])
        models = {}
        for model in freeze['model_digests']:
            rows = [r for r in data['results'] if r['job']['model'] == model]
            models[model] = {'requests':len(rows), 'raw_server_expected_calls':sum(r['server_native_calls']==[r['job']['expected']] for r in rows),
                'after_adapter_expected_calls':sum(r['expected_call_match'] for r in rows)}
        result = {'date':'2026-11-17','requests':48,'extra_requests':0,'offline_replays':35,
            'model_summary':models,'usage':data['usage'],'archive_files':file_count,
            'original_archive_files':original_files,'frozen_source_files':len(freeze['files']),
            'old_69_source_hashes_pass':True,'model_digest_matches_pass':True,
            'all_archive_hashes_pass':True,'server_call_names_counts_preserved':calls_preserved,
            'argument_normalizations':normalizations,'raw_vs_adapter_probe_pairs':12,
            'probe_pair_body_differences':'Only omission of empty images arrays.',
            'raw_server_calls_are_already_ollama_parsed':True,
            'wire_stream_default_reproduced':zero['wire_stream_from_constructor_streaming_false'],
            'wire_stream_false_when_explicit':zero['wire_stream_with_explicit_stream_false'],
            'archive_sha256':sha(path.read_bytes())}
        (EVIDENCE/'INDEPENDENT_INTEGRATION_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
        (EVIDENCE/'RECONCILED_RESULTS.json').write_text(json.dumps(data,indent=2)+'\n')
        table = []
        for r in data['results']:
            table.append(f'| {r["job"]["id"]} | {r["job"]["model"]} | {r["server_native_calls"]==[r["job"]["expected"]]} | {r["expected_call_match"]} |')
        report = '''# Llama and Granite: completed integration investigation

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
'''
        report += '\n'.join(table) + '\n\n'
        report += f'Input tokens: **{data["usage"]["prompt_eval_count"]:,}**. Output tokens: **{data["usage"]["eval_count"]:,}**. Verified outer content files: **{file_count}**; nested original content files: **{original_files}**.\n\n'
        report += f'Evidence SHA-256: `{sha(path.read_bytes())}`.\n'
        (EVIDENCE/'INTEGRATION_FINDINGS_2026-11-17.md').write_text(report,encoding='utf-8')
    print(json.dumps({'requests':48,'normalizations':len(normalizations),'verified_files':file_count,'model_summary':models},indent=2))


if __name__=='__main__':
    main()
