"""New lab replication adapter; historical experiment source stays byte-identical."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path('/work')
RESULTS = ROOT / 'results'
STUDY = ROOT / 'study'
ENDPOINT = 'http://127.0.0.1:11439'
PROJECT = 'rosa-lab-multimodel-20261117'
MODELS = ['qwen3.5:9b', 'llama3.1:8b-instruct-q4_K_M', 'granite3.3:8b',
          'ministral-3:8b-instruct-2512-q4_K_M']
ORDER = list(MODELS)
random.Random(20261117).shuffle(ORDER)


def key(model):
    return model.replace(':', '_')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def api(path, data=None, timeout=30):
    request = Request(ENDPOINT + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def schedule(model):
    from experiments.macro_m4.design import cases
    specifications = cases()
    result = []
    for repetition in range(1, 5):
        rotation = ((repetition - 1) * 5) % len(specifications)
        ordered = specifications[rotation:] + specifications[:rotation]
        for index, spec in enumerate(ordered):
            first_macro = (index + repetition) % 2 == 0
            for condition in (('macro', 'primitives') if first_macro else ('primitives', 'macro')):
                result.append({'id': f'{len(result)+1:02d}-{spec["id"]}-r{repetition}-{condition}',
                    'case': deepcopy(spec), 'repetition': repetition, 'condition': condition})
    assert len(result) == 80
    assert len({r['id'] for r in result}) == 80
    assert sum(r['condition'] == 'macro' for r in result) == 40
    assert sum(r['case']['kind'] == 'clarification' for r in result) == 8
    return result


def freeze():
    if (STUDY / 'freeze.json').exists():
        raise RuntimeError('Freeze already exists; refusing replacement')
    original = json.loads((ROOT / 'baseline/original-m4-freeze.json').read_text())
    files = {}
    for name, expected in original['files'].items():
        path = ROOT / 'baseline' / name
        if sha(path) != expected:
            raise RuntimeError('Original M4 source mismatch: ' + name)
        files[str(path.relative_to(ROOT))] = expected
    for path in sorted(STUDY.rglob('*')):
        if path.is_file():
            files[str(path.relative_to(ROOT))] = sha(path)
    tags = api('/api/tags')['models']
    selected = {m: next(x for x in tags if x['name'] == m) for m in MODELS}
    expected_qwen = '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90'
    write(STUDY / 'freeze.json', {'files': files, 'model_metadata': selected,
        'same_qwen_digest_as_m4': selected[MODELS[0]]['digest'] == expected_qwen,
        'server': api('/api/version'), 'model_order': ORDER,
        'schedule': schedule(MODELS[0]), 'planned_trials': 320,
        'requests_per_model': 643, 'per_model_seconds': 28800,
        'clarification_semantics': 'HUMAN_REVIEW_PENDING',
        'context': 8192, 'output_per_call': 1024, 'output_per_task': 2048,
        'temperature': 0, 'seed': 42, 'source_commits': original.get('source_commits'),
        'frozen_at_unix': time.time()})
    print('FROZEN', len(files), 'files;', len(schedule(MODELS[0])), 'trials per model', flush=True)


def verify():
    record = json.loads((STUDY / 'freeze.json').read_text())
    for name, expected in record['files'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Replication source changed: ' + name)
    return record


def configure(model):
    from experiments.macro_m4 import runner, design, recovery
    from experiments.macro_capabilities_v2 import observability
    design.LIMITS.update(repetitions=4, backend_requests=643)
    assert recovery.LIMITS is design.LIMITS
    observability.PROJECT = PROJECT
    runner.BASE = RESULTS / key(model)
    runner.BASE.mkdir(parents=True, exist_ok=True)
    runner.verify = verify
    runner.jobs = lambda backend: schedule(model)
    original_trace = runner.trace_check

    @contextmanager
    def trace(path, metadata):
        with original_trace(path, {**metadata, 'stage': 'LAB_MULTIMODEL',
                'model': model, 'study': PROJECT}) as tracer:
            yield tracer
    runner.trace_check = trace
    original_write = runner.write

    def annotated_write(path, value):
        if path.name == 'checkpoint.json':
            value['planned'] = 20 if value.get('backend') == 'deterministic' else 80
            value['study'] = PROJECT
            value['model'] = model
        elif path.name == 'outside-task-ollama-status.json':
            try:
                value = {'models': [x for x in api('/api/ps').get('models', []) if x['name'] == model]}
            except Exception as error:
                value = {'error_type': type(error).__name__}
        original_write(path, value)
    runner.write = annotated_write

    def persisted(folder):
        command = "import experiments.macro_capabilities_v2.persisted as p; p.PROJECT=" + repr(PROJECT) + "; p.main()"
        result = subprocess.run([str(ROOT / 'runtime/envs/phoenix/bin/python'), '-B', '-c', command,
            '--folder', str(folder)], cwd=ROOT / 'baseline/rosa-evaluation',
            capture_output=True, text=True, timeout=60)
        (folder / 'phoenix-audit.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError('persisted_phoenix_audit_failed')
        return json.loads((folder / 'phoenix-audit.json').read_text())
    runner.persisted = persisted
    os.environ.update(ROS_DOMAIN_ID='229', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST',
        LANGCHAIN_TRACING='false', LANGCHAIN_TRACING_V2='false', LANGSMITH_TRACING='false')
    return runner


def configured_model(model, max_output=1024, journal=None):
    from pydantic import PrivateAttr
    from rosa_backends.chat_ollama import ConfiguredChatOllama

    class MeasuredChat(ConfiguredChatOllama):
        _records: list = PrivateAttr(default_factory=list)

        def _generate(self, *args, **kwargs):
            started = time.monotonic()
            row = {'physical_call': len(self._records) + 1, 'status': 'STARTED'}
            self._records.append(row)
            try:
                result = super()._generate(*args, **kwargs)
                message = result.generations[0].message
                row.update(status='RETURNED', response_metadata=message.response_metadata,
                    usage=message.usage_metadata, tool_call_count=len(message.tool_calls or []))
                return result
            except Exception as error:
                row.update(status='ERROR', error_type=type(error).__name__,
                    http_status=getattr(error, 'status_code', None))
                raise
            finally:
                row['wall_seconds'] = time.monotonic() - started
                if journal:
                    write(journal, self._records)

    metadata = json.loads((ROOT / 'preparation' / ('model-' + key(model) + '.json')).read_text())
    return MeasuredChat(model=model, base_url=ENDPOINT, num_ctx=8192,
        num_predict=max_output, temperature=0, seed=42, use_mmap=True,
        streaming=False, reasoning=False if 'thinking' in metadata.get('capabilities', []) else None,
        cache=False, client_kwargs={'timeout': 180})


def controls():
    runner = configure('deterministic')
    result = runner.run('deterministic', control=True)
    if (result['status'] != 'COMPLETE' or result['primary_correct'] != 20 or
            result['simulator_cleanup']['returncode'] != 0 or result['cleanup_errors'] or
            not all(r['phoenix_audit']['pass'] for r in result['trials'])):
        raise RuntimeError('Deterministic controls failed')


def gpu_gate(model):
    # This container runs CPU-only Gazebo. The host orchestrator checks the GPU
    # used by the separate localhost Ollama service immediately before launch.
    record = json.loads((ROOT / 'preparation' / ('gpu-' + key(model) + '.json')).read_text())
    if record['model'] != model or not 0 <= time.time() - record['at_unix'] <= 120:
        raise RuntimeError('GPU preflight is missing or stale')
    write(RESULTS / key(model) / 'gpu-preflight.json', record)
    if not record['pass']:
        raise RuntimeError('GPU gate not passed; no competing jobs will be stopped')


def run(model):
    verify()
    check = json.loads((RESULTS / 'deterministic/controls/checkpoint.json').read_text())
    if check['status'] != 'COMPLETE' or check['primary_correct'] != 20:
        raise RuntimeError('Controls not passed')
    gpu_gate(model)
    runner = configure(model)
    journal = RESULTS / key(model) / 'physical-model-calls.json'
    agent_model = configured_model(model, journal=journal)
    try:
        runner.run('ollama', model=agent_model, endpoint=ENDPOINT)
    finally:
        try:
            write(RESULTS / key(model) / 'unload.json',
                api('/api/generate', {'model': model, 'keep_alive': 0}, timeout=60))
        except Exception as error:
            write(RESULTS / key(model) / 'unload.json', {'error_type': type(error).__name__})


def report():
    summary = {'study': PROJECT, 'model_order': ORDER, 'models': {},
        'note': 'Known-goal correctness excludes pending human clarification judgments. Historical Sol is not a fresh lab run.'}
    table = []
    for model in MODELS:
        checkpoint = RESULTS / key(model) / 'ollama/checkpoint.json'
        if not checkpoint.exists():
            summary['models'][model] = {'status': 'UNSTARTED', 'planned': 80}
            continue
        data = json.loads(checkpoint.read_text())
        rows = data['trials']
        model_summary = {'status': data['status'], 'planned': 80, 'recorded': len(rows),
            'current_trial': data.get('current_trial'), 'campaign': data.get('campaign'),
            'cleanup': data.get('simulator_cleanup'), 'conditions': {}, 'paired_known_goal': {}}
        for condition in ('primitives', 'macro'):
            selected = [r for r in rows if r['condition'] == condition]
            known = [r for r in selected if r['case'] != 'ambiguous_goal']
            ambiguous = [r for r in selected if r['case'] == 'ambiguous_goal']
            values = {'recorded': len(selected), 'planned': 40,
                'known_goal_correct': sum(r['primary_pass'] for r in known),
                'known_goal_recorded': len(known), 'known_goal_planned': 36,
                'clarification_semantics': 'HUMAN_REVIEW_PENDING', 'ambiguous_recorded': len(ambiguous),
                'legacy_regex_passes': sum(r['primary_pass'] for r in ambiguous),
                'model_calls': sum(r['inference']['calls'] for r in selected),
                'known_input_tokens': sum(r['inference']['known_input_tokens'] for r in selected),
                'known_output_tokens': sum(r['inference']['known_output_tokens'] for r in selected),
                'unknown_usage_trials': sum(not r['inference']['usage_complete'] for r in selected),
                'native_operations': sum(r['score']['native_operations'] for r in selected),
                'task_seconds': sum(r['wall_seconds'] for r in selected),
                'mean_task_seconds': statistics.mean(r['wall_seconds'] for r in selected) if selected else None,
                'median_task_seconds': statistics.median(r['wall_seconds'] for r in selected) if selected else None,
                'invalid_attempts': sum(r['score']['invalid_attempts'] for r in selected),
                'unsupported_success_attempts': sum(r['score']['unsupported_success_attempts'] for r in selected),
                'accepted_wrong_goal_successes': sum(r['score']['accepted_success_wrong_user_goal'] for r in selected),
                'dispatch_violations': sum(bool(r['score']['dispatch_violations']) for r in selected),
                'error_types': {}, 'families': {}}
            for row in selected:
                error = row.get('error_type')
                if error:
                    values['error_types'][error] = values['error_types'].get(error, 0) + 1
                family = values['families'].setdefault(row['case'], {'n': 0, 'legacy_pass': 0})
                family['n'] += 1
                family['legacy_pass'] += int(row['primary_pass'])
            model_summary['conditions'][condition] = values
            timing = f'{values["mean_task_seconds"]:.2f}' if values['mean_task_seconds'] is not None else 'NOT_RECORDED'
            table.append(f'| {model} | {condition} | {values["known_goal_correct"]}/{values["known_goal_recorded"]} | {values["model_calls"]} | {timing} | {values["native_operations"]} |')
        pairs = {}
        for row in rows:
            if row['case'] != 'ambiguous_goal':
                pairs.setdefault((row['case'], row['repetition']), {})[row['condition']] = row
        complete_pairs = [p for p in pairs.values() if len(p) == 2]
        both = [p for p in complete_pairs if all(r['primary_pass'] for r in p.values())]
        model_summary['paired_known_goal'] = {'complete_pairs': len(complete_pairs),
            'macro_only_correct': sum(p['macro']['primary_pass'] and not p['primitives']['primary_pass'] for p in complete_pairs),
            'primitive_only_correct': sum(p['primitives']['primary_pass'] and not p['macro']['primary_pass'] for p in complete_pairs),
            'matched_success_pairs': len(both),
            'matched_success_calls': {c: sum(p[c]['inference']['calls'] for p in both) for c in ('primitives','macro')},
            'matched_success_native': {c: sum(p[c]['score']['native_operations'] for p in both) for c in ('primitives','macro')},
            'matched_success_seconds': {c: sum(p[c]['wall_seconds'] for p in both) for c in ('primitives','macro')}}
        summary['models'][model] = model_summary
    write(RESULTS / 'analysis.json', summary)
    text = '# Lab local-model comparison — 2026-11-17\n\n'
    text += 'New replication of known M4 cases. 80 scheduled trials per model; four repetitions, two conditions.\n\n'
    text += '| Model | Condition | Known-goal correct/recorded | Calls | Mean task seconds | Native ops |\n|---|---|---:|---:|---:|---:|\n' + '\n'.join(table)
    text += '\n\nEight ambiguous trials per model need actual human semantic review; the known-goal denominator is 72 per completed model. The legacy regex scores are diagnostic, not an adjudication.\n'
    text += '\nAll-attempt costs include failed tasks. Matched-success and family details are in analysis.json. No broad reliability, generalization, equivalence or physical-safety claim follows. Compare against fresh lab Qwen; historical Sol and laptop Qwen differ in hardware, repetitions and environment.\n'
    (RESULTS / 'COMPARISON_REPORT.md').write_text(text)
    print(json.dumps({m: {'status': s['status'], 'recorded': s.get('recorded', 0)} for m,s in summary['models'].items()}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'controls', 'run', 'report'])
    parser.add_argument('--model', choices=MODELS)
    args = parser.parse_args()
    if args.action == 'freeze':
        freeze()
    elif args.action == 'controls':
        controls()
    elif args.action == 'run':
        if not args.model:
            parser.error('--model required')
        run(args.model)
    else:
        report()


if __name__ == '__main__':
    main()
