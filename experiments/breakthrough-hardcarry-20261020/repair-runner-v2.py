"""Repair fixture environment only. Frozen runtime source remains unchanged."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE_FREEZE.json').read_text());t=r/'observer'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(r/'run.exit').read_text().strip()=='101'
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
failed=r/'failed-missing-fixture-environment-v1';failed.mkdir(exist_ok=False)
for name in['tests.log','run.exit','run.sh','SOURCE_FREEZE.json','source.patch']:shutil.copyfile(r/name,failed/name)
log=(r/'tests.log').read_text();assert log.count('hard carry cap: NotPresent')>=2
assert'test result: ok. 5 passed; 0 failed;'in log and'test result: ok. 4 passed; 0 failed;'in log
(r/'RUNNER-REPAIR.json').write_text(json.dumps({'status':'FROZEN_SOURCE_UNCHANGED','source_freeze_sha256':sha(r/'SOURCE_FREEZE.json'),'reason':'Unit fixtures do not call the full build entry that establishes HARD_CARRY_CAP. Supply accepted1234 to fixture processes; generation still sets its declared BREAK_HARD per case.','no_arithmetic_or_gate_change':True},indent=2)+'\n')
