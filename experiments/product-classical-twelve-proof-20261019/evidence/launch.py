import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;n=r.parent/'product-classical-twelve-native-20261019'
assert (n/'run.exit').read_text().strip()=='0' and not (r/'run.pid').exists()
with (r/'nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'independent-three-additional-factor-proofs'}))
