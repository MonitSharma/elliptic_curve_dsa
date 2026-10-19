import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'build.pid').exists() and not (r/'watch.pid').exists()
for name,cmd in [('build',['nohup','bash','run-build.sh']),('watch',['nohup','python3','after_gate.py'])]:
    with (r/(name+'-nohup.log')).open('xb') as f:
        p=subprocess.Popen(cmd,cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    (r/(name+'.pid')).write_text(str(p.pid)+'\n');print(json.dumps({'kind':name,'pid':p.pid}))
