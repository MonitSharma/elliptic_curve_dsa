import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'prepare-v2.exit').read_text().strip()=='0'
assert not (r/'search.pid').exists() and not (r/'run-record.json').exists()
with (r/'search.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-search.sh'],cwd=r,stdin=subprocess.DEVNULL,
        stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'search.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'ascending-search'}))
