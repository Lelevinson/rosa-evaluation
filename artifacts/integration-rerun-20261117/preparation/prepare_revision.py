"""Prepare documented fixture-contract revision; never changes first freeze."""
from pathlib import Path
import ast
import zipfile

old=Path(__file__).resolve().parent
new=old.parents[1]/'integration-rerun-20261117-r1/preparation'
new.mkdir(parents=True,exist_ok=True)
names=['tool_contract_ollama.py','campaign.py','operator_run.py','test_profile.py','PROTOCOL.md']
for name in names:
    target=new/name
    assert not target.exists(),target
    target.write_bytes((old/name).read_bytes())
p=new/'campaign.py';text=p.read_text(encoding='utf-8')
text=text.replace("BASE=ROOT/'integration-rerun-20261117'",'BASE=Path(__file__).resolve().parents[1]')
text=text.replace('return {name:self.ready for name in names}','return {name:bool(self.ready) for name in names}')
p.write_bytes(text.encode())
p=new/'operator_run.py'
p.write_bytes(p.read_bytes().replace(b'integration-rerun-20261117',b'integration-rerun-20261117-r1'))
p=new/'test_profile.py';text=p.read_text(encoding='utf-8')
marker='    def test_original_backend_and_strict_reporting_unchanged(self):'
extra='''    def test_fixture_inspection_returns_required_booleans(self):
        from campaign import FixtureInspection
        self.assertIs(FixtureInspection(1.0).read_group("health",["ready"])["ready"],True)
        self.assertIs(FixtureInspection(0.0).read_group("health",["ready"])["ready"],False)

'''
assert marker in text
p.write_bytes(text.replace(marker,extra+marker).encode())
p=new/'PROTOCOL.md'
note='''## Revision 1 amendment - 2026-11-17

The initial deterministic inspection control failed before any model requests because the mock returned float readiness values while the existing interface requires bool. Preserve the original stopped folder, failed control, source freeze and raw archive. This revision converts the fixture return value to bool, adds a zero-network fixture-contract test and uses a separate output root. The profile, model prompts/tasks, scoring criteria, model identities and resource limits are unchanged. No model outcomes were available for tuning and no model trial was retried.

'''
p.write_bytes((note+p.read_text(encoding='utf-8')).encode())
for name in names:
    if name.endswith('.py'):ast.parse((new/name).read_text(encoding='utf-8'))
with zipfile.ZipFile(new/'campaign-source-r1.zip','x',zipfile.ZIP_DEFLATED) as out:
    for name in names:out.write(new/name,name)
print('Revision 1 source package ready',new)
