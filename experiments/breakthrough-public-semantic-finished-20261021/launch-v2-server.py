import hashlib,json,os,socket,subprocess
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/breakthrough-public-semantic-finished-20261021')
assert socket.gethostname()=='LHC-104-070' and not(r/'pipeline-v2.pid').exists()
assert int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1])>100*1024**2
assert not(r.parent/'breakthrough-public-semantic-final-gate-20261021/GATE-DECLARATION.json').exists()
with(r/'pipeline-v2.log').open('xb')as out:
 p=subprocess.Popen(['nohup','python3','-u',str(r/'server-run-v2.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'pipeline-v2.pid').write_text(str(p.pid)+'\n')
v={'pid':p.pid,'source_revision':json.loads((r/'SOURCE-FREEZE.json').read_text())['source_revision'],'driver_sha256':hashlib.sha256((r/'server-run-v2.py').read_bytes()).hexdigest(),'scope':'Unchanged source, original setup failure preserved. No earlier gate declared.'}
(r/'SERVER-LAUNCH-V2.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
