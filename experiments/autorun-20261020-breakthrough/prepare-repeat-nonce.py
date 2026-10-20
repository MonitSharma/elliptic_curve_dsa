"""Adapt the already qualified exact nonce engine to the new frozen circuit."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-public8b-repeat-nonce-20261020';r.mkdir(exist_ok=True)
s=(root/'experiments/autorun-20261020-breakthrough/run-exact154-nonce.py').read_text()
changes={'breakthrough-public140-exact154-20261020':'breakthrough-public8b-repeat-generic-20261020','breakthrough-public140-exact154-final-gate-20261020':'breakthrough-public8b-repeat-final-gate-20261020','public140-exact154-final-20261020-v1':'public8b-repeat-generic-final-20261020-v1','7b165a67d95bdfadc274ddf303bf7a092c63d1d42bf223510e81d628be88fb3e':'4fb7a65acb7027fe9fa519b0db781f830c5cf1e1e5573afa102247401b3b6a01','SOURCE-FREEZE.json':'SOURCE-FREEZE-v2.json'}
for a,b in changes.items():assert a in s;s=s.replace(a,b)
(r/'run.py').write_bytes(s.encode());(r/'.gitignore').write_bytes(b'/tool/\n/target/\n/__pycache__/\n*resource-preflight*\n/evidence.tar.gz\n');(r/'.gitattributes').write_bytes(b'* -text\n')
subprocess.run(['ssh','smu_server','mkdir /home/hclau/ecdsa_research/breakthrough-public8b-repeat-nonce-20261020'],check=True);subprocess.run(['scp',str(r/'run.py'),'smu_server:/home/hclau/ecdsa_research/breakthrough-public8b-repeat-nonce-20261020/'],check=True)
