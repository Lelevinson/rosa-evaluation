"""Record an explicit clean rerun without changing benchmark contracts or results."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

from .config import ROOT, checkout

CAMPAIGN = ROOT.parent / 'reports/clean-stage1-4-20261021-r1'
RESEARCH = checkout('research')
PYTHON = str((RESEARCH / '.venv').resolve() / 'bin/python')


def utc():
    return datetime.now(timezone.utc).isoformat()


def sources():
    result = {}
    for repo in (ROOT, RESEARCH):
        candidates = []
        for folder in ('src', 'experiments', 'tests', 'tools', 'scripts'):
            directory = repo / folder
            if directory.exists():
                candidates += [p for p in directory.rglob('*') if p.is_file()
                    and p.suffix in ('.py', '.sh', '.ps1', '.toml', '.lock')
                    and not any(part in ('.venv', '__pycache__') for part in p.relative_to(repo).parts)]
        candidates += [repo / name for name in ('README.md', 'pyproject.toml', 'uv.lock',
                         '.python-version', '.env.example', 'config.toml', 'run.sh', '.gitattributes')
                       if (repo / name).is_file()]
        for path in sorted(set(candidates)):
            result[str(path.relative_to(ROOT.parent))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def load():
    path = CAMPAIGN / 'campaign.json'
    return json.loads(path.read_text()) if path.exists() else {
        'campaign': CAMPAIGN.name, 'started_utc': utc(), 'status': 'IN_PROGRESS', 'steps': {},
        'scope': 'Fresh execution of existing 12-scenario live pilot and 60-scenario scripted control',
        'old_results_preserved': True, 'live_backends_sequential': True,
        'prompt_or_controller_tuning': False, 'jtvr': False, 'episodic_memory': False,
        'trial_deadline_seconds': 240, 'calls_per_trial': 14,
        'request_ceiling_per_live_batch': 840, 'inference_wall_ceiling_per_live_batch': 7200,
        'live_trials_per_backend': 60, 'live_distinct_scenarios': 12,
        'scripted_trials': 540, 'scripted_distinct_scenarios': 60,
        'source_sha256_at_start': sources()}


def save(data):
    (CAMPAIGN / 'campaign.json').write_text(json.dumps(data, indent=2) + '\n')


def run(name, command, cwd=ROOT):
    data = load()
    if name in data['steps']:
        raise RuntimeError(f'Step already exists: {name}; preserve it and choose an explicit new campaign for retries')
    record = {'started_utc': utc(), 'command': command, 'cwd': str(cwd), 'status': 'RUNNING'}
    data['steps'][name] = record
    save(data)
    started = time.monotonic()
    lines = []
    with (CAMPAIGN / f'{name}.log').open('w') as log:
        process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, bufsize=1)
        record['pid'] = process.pid
        save(data)
        for line in process.stdout:
            log.write(line)
            log.flush()
            lines.append(line)
            print(line, end='', flush=True)
            match = re.search(r'/runs/([0-9a-f-]{36})/result\.json', line)
            if match:
                record['run_id'] = match.group(1)
                save(data)
            match = re.search(r'rosa-validation-[0-9a-f]{8}', line)
            if match:
                record['validation_project'] = match.group()
                save(data)
        record['returncode'] = process.wait()
    record.update(ended_utc=utc(), wall_seconds=time.monotonic() - started,
                  status='COMMAND_PASSED' if record['returncode'] == 0 else 'COMMAND_FAILED')
    data['source_sha256_current'] = sources()
    data['source_changes_since_start'] = [key for key, value in data['source_sha256_at_start'].items()
                                         if data['source_sha256_current'].get(key) != value]
    save(data)
    print(f'Campaign step {name}: {record["status"]}', flush=True)
    return record['returncode']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['init', 'offline', 'offline-jazzy', 'native', 'shared-local', 'scripted',
                                        'hosted', 'local', 'audit-scripted', 'audit-hosted', 'audit-local', 'inspect-readiness'])
    args = parser.parse_args()
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    data = load()
    save(data)
    if args.phase == 'init':
        for relative in data['source_sha256_at_start']:
            target = CAMPAIGN / 'source' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT.parent / relative, target)
        for repo in (ROOT, RESEARCH):
            diff = subprocess.check_output(['git', '-C', str(repo), 'diff', '--no-ext-diff'], text=True)
            (CAMPAIGN / f'{repo.name}.patch').write_text(diff)
            data[repo.name + '_commit'] = subprocess.check_output(
                ['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        save(data)
        print(f'Frozen campaign: {CAMPAIGN}')
        return 0
    if args.phase in ('offline', 'offline-jazzy'):
        research_check = (('research-jazzy-unit', ['bash', str(CAMPAIGN / 'research-tests.sh')], RESEARCH)
                          if args.phase == 'offline-jazzy' else
                          ('research-unit', [PYTHON, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], RESEARCH))
        checks = [research_check,
                  ('evaluation-unit', [PYTHON, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], ROOT),
                  ('phoenix-smoke', ['bash', 'tools/phoenix/run.sh', 'smoke'], ROOT),
                  ('phoenix-validation', ['bash', 'tools/phoenix/run.sh', 'validate'], ROOT)]
        for name, command, cwd in checks:
            code = run(name, command, cwd)
            if code:
                return code
        return 0
    if args.phase.startswith('audit-'):
        backend = args.phase.split('-', 1)[1]
        identifier = data['steps'][backend]['run_id']
        return run(args.phase, ['bash', 'tools/phoenix/run.sh', 'audit', '--batch-id', identifier]
                   + (['--oracle-only'] if backend == 'scripted' else []))
    if args.phase == 'inspect-readiness':
        for step in ('native', 'shared-local'):
            code = run('inspect-' + step, ['bash', 'tools/phoenix/run.sh', 'inspect',
                                          '--run-id', data['steps'][step]['run_id']])
            if code:
                return code
        return 0
    commands = {
        'native': ['--probe-qwen', '--num-ctx', '4096', '--use-mmap'],
        'shared-local': ['--probe-backends', '--backend', 'ollama', '--use-mmap'],
        'scripted': ['--benchmark', '--backend', 'scripted', '--suite', 'full', '--repeats', '3', '--tracing', 'off'],
        'hosted': ['--benchmark', '--backend', 'siwc', '--suite', 'pilot', '--repeats', '3', '--request-budget', '840', '--model', 'gpt-6.1-sol'],
        'local': ['--benchmark', '--backend', 'ollama', '--suite', 'pilot', '--repeats', '3', '--request-budget', '840'],
    }
    return run(args.phase, ['bash', 'run.sh', 'research'] + commands[args.phase])


if __name__ == '__main__':
    raise SystemExit(main())
