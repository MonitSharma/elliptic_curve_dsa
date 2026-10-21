import json,subprocess
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/breakthrough-public-semantic-nonce-20261021');assert not(r/'run.pid').exists()
with(r/'run.log').open('xb')as out:p=subprocess.Popen(['nohup','python3','-u',str(r/'run.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'root':str(r)}))
