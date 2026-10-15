"""Continue the predeclared second case after its immutable prerequisite exists."""
from pathlib import Path
import json,subprocess
r=Path(__file__).resolve().parent
assert (r/'original4b.exit').read_text().strip()=='0'
assert not (r/'product95-launch.pid').exists() and not (r/'product95.exit').exists()
assert (r.parent/'product-exact-20261015/PRODUCT95_FREEZE.json').exists()
pre=json.loads(subprocess.check_output(['python3','/home/hclau/ecdsa_research/server-preflight.py']))
assert pre['hostname']=='LHC-104-070' and pre['memory']['MemAvailable_bytes']>=116*1024**3
(r/'product95-preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
with (r/'product95-launch.log').open('w') as out:
    p=subprocess.Popen(['nohup','python3',str(r/'case.py'),'product95'],cwd=r,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'product95-launch.pid').write_text(str(p.pid)+'\n');print(p.pid)
