import json,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'run-v3.pid').exists()
assert not (r/'reordered.ops.bin').exists()
for name in ('tests.log','nohup-v2.log','preflight-v2.json','SOURCE-v2.sha256','STOP-V2.json','run-v2.exit'):
    p=r/name
    if p.exists():
        dest=r/'stopped-v2'/name;dest.parent.mkdir(exist_ok=True);assert not dest.exists();dest.write_bytes(p.read_bytes())
with (r/'nohup-v3.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-v3.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run-v3.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'reset-and-measurement-RNG-preserving-exact-scheduling'}))
