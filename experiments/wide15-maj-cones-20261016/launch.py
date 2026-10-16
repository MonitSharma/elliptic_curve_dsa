from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parent
assert not(R/'launcher.pid').exists()
d=json.loads((R/'DECLARATION.json').read_text())
for name,h in d['code_and_reference_pins'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name
p=json.loads(subprocess.check_output(['python3','/home/hclau/ecdsa_research/server-preflight.py']))
assert p['hostname']=='LHC-104-070' and p['memory']['MemAvailable_bytes']>=112*1024**3
(R/'preflight.json').write_text(json.dumps(p,indent=2)+'\n')
with(R/'run.log').open('x')as log:
 proc=subprocess.Popen(['nohup','setsid','bash',str(R/'run.sh')],cwd=R,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
(R/'launcher.pid').write_text(str(proc.pid)+'\n')
print(json.dumps({'pid':proc.pid,'max_threads':1,'max_GiB':12,'wall_seconds':900}))
