import json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;assert (r/'run.exit').read_text().strip()=='1'
assert 'LOCAL-VERIFICATION.json' in (r/'nohup.log').read_text()
assert not (r/'COMMANDS.json').exists() and not (r/'compiler-version.log').exists()
dest=r/'failed-admission-v1';dest.mkdir(exist_ok=False)
for name in ['run.pid','run.exit','LAUNCH.json','SOURCE.sha256','nohup.log']:shutil.move(r/name,dest/name)
for p in [*r.glob('*.py'),*r.glob('*.rs'),*r.glob('*.sh'),r/'PREPARATION.json']:shutil.copy2(p,dest/p.name)
shutil.copytree(r/'proof',dest/'proof')
note={'status':'LOCAL_RUNTIME_VERIFICATION_NOT_YET_FINISHED_ADMISSION_FAILURE','compiler_invoked':False,'source_scan_started':False,'gate_or_nonce_started':False,'preserved_directory':dest.name,'repair':'Launcher now verifies the completed runtime receipt before starting a job.'}
(r/'ADMISSION-REPAIR.json').write_text(json.dumps(note,indent=2)+'\n')
