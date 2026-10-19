import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'watch.pid').exists()
with (r/'watch.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','python3','watch.py'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'watch.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'queue-only-terminal-audit-and-native-benchmark'}))
