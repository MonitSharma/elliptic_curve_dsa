import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'run.pid').exists() and not (r/'run.exit').exists()
assert (r.parent/'resource-registry-20261020'/(r.name+'-run.json')).exists()
with (r/'nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'pinned-native-copy-cache-reproduction','slots':1,'nonce_screen':False}))
