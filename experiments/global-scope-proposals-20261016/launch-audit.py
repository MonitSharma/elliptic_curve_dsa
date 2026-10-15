from pathlib import Path
import json,subprocess
r=Path(__file__).resolve().parent
assert not (r/'audit-launch.pid').exists()
pre=json.loads(subprocess.check_output(['python3','/home/hclau/ecdsa_research/server-preflight.py']))
assert pre['hostname']=='LHC-104-070' and pre['memory']['MemAvailable_bytes']>=104*1024**3
(r/'audit-preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
with (r/'audit-launch.log').open('w') as out:
    p=subprocess.Popen(['nohup','bash',str(r/'audit-run.sh')],cwd=r,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'audit-launch.pid').write_text(str(p.pid)+'\n');print(p.pid)
