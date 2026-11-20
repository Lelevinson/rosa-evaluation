"""Verify pinned reference bytes and record the owner's prospective adoption."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE.parents[1]
WORKSPACE = EVAL.parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    refs = {}
    expected = {'RESEARCH_RULES.md': '3f1580f0dbf8cd20170be2f12eb43a6d3d1bf2cb',
        'ROSA_RESEARCH_CONTEXT.md': '35b276eb1162586676763a5f32f8cd76dd04b062'}
    for name, blob in expected.items():
        data = (HERE / 'reference' / name).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert actual == blob, (name, actual)
        refs[name] = {'git_blob_sha1': actual, 'sha256': sha(data), 'bytes': len(data)}
    master = EVAL / 'PROJECT_MASTER_README.md'
    prior = master.read_bytes()
    backup = HERE / 'PROJECT_MASTER_BEFORE_ADOPTION.md'
    assert not backup.exists(), 'Preserve previous context snapshots'
    backup.write_bytes(prior)
    text = prior.decode('utf-8').replace('\r\n', '\n')
    marker = '**Latest completed work - native-schema integration and robot reruns, 2026-11-17.**'
    assert marker in text
    addition = '''**Research standards adopted - 2026-11-17.**
The owner explicitly asked this assistant to follow the stable research rules
**provided by teammate Levinson** through `rosa-contexts`. The operative local
[adopted rules](docs/research-governance-20261117/ADOPTED_RESEARCH_RULES.md) and
[dated adoption record](docs/research-governance-20261117/ADOPTION_RECORD.md) are
now referenced by the workspace `AGENTS.md`. Before substantial future research
work, use the full five-question preflight: closest mechanism and actual
difference; observed need and honest denominators; concrete decision and
discriminator; genuinely capable fair controls without a hidden oracle; and the
smallest nonrepeating decision-changing next step. Preserve protocols, failures,
negative findings, complete cost accounting, evidence provenance and review gates.

This is a prospective governance change, not a new study or a retrospective claim
of full compliance. Martin's practical ROSA reliability/efficiency vision remains
the project direction; teammate-specific deadlines, language preferences and
historical launch decisions are attributed context. No experiment, runtime,
scorer, frozen result or G1 gate changed. Earlier experiment ZIPs retain the
master snapshot at their packaging time; they are not rewritten to include this
later policy update. The [source provenance](docs/research-governance-20261117/SOURCE_PROVENANCE.json)
pins the adopted upstream version and verifies both saved source files.

'''
    text = text.replace(marker, addition + marker, 1)
    master.write_text(text, encoding='utf-8', newline='\n')
    record = {'date': '2026-11-17', 'owner_authorized_adoption': True,
        'source_provided_by': 'Teammate Levinson', 'repository': 'Lelevinson/rosa-contexts',
        'branch': 'member/levinson', 'commit': '76481368e1a2abff12147f89bde3bf54620ef3f5',
        'source_files': refs, 'canonical_sections_read': ['0-4', '8', '11', '12', '14', '15', '24'],
        'upstream_AGENTS_md_available': False, 'prospective_adoption': True,
        'experimental_model_requests': 0, 'runtime_or_frozen_result_changes': 0,
        'git_publication': False, 'master_before_sha256': sha(prior),
        'master_after_sha256': sha(master.read_bytes()),
        'workspace_instructions_sha256': sha((WORKSPACE / 'AGENTS.md').read_bytes())}
    (HERE / 'SOURCE_PROVENANCE.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
