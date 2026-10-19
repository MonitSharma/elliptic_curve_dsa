"""Preserve the refused pre-build attempt; retry after the named job ends."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-classical-twelve-operational-20261019';native=ws/'product-copy-cache-native-20261020'
assert (r/'prepare.exit').read_text().strip()=='1' and not (r/'tool').exists() and not (r/'prepare.log').exists()
assert 'registered PID cwd/entrypoint mismatch' in (r/'prepare-nohup.log').read_text()
assert (native/'run.exit').read_text().strip()=='0'
pid=int((native/'run.pid').read_text());p=Path('/proc')/str(pid)
if (p/'status').exists():assert next(x.split()[1] for x in (p/'status').read_text().splitlines() if x.startswith('State:'))=='Z'
d=r/'failed-admission-v1';d.mkdir(exist_ok=False)
for name in ['prepare.pid','prepare.exit','prepare-preflight.json','prepare-nohup.log']:shutil.move(r/name,d/name)
for p in r.iterdir():
    if p.is_file() and p.suffix in ['.py','.sh']:shutil.copy2(p,d/p.name)
note={'at_utc':datetime.now(timezone.utc).isoformat(),'status':'PRE_BUILD_RESOURCE_IDENTITY_REFUSAL_PRESERVED','cause':'Strict descriptor cwd rule refused another registered native leader after that shell entered its candidate subdirectory. The native job has now completed successfully.','source_code_changed':False,'old_attempt_started_build_or_nonce':False,'statistical_gate_repeated':False,'retry':'Same reviewed operational preparation after the actual incompatible live process ended. Future dynamic leaders must retain root cwd while children use subdirectories.'}
(r/'ADMISSION-REPAIR.json').write_text(json.dumps(note,indent=2)+'\n')
subprocess.run(['python3',str(r/'launch_prepare.py')],check=True)
