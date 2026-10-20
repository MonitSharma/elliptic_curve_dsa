"""Prepare final source/benchmark controller; wait for the fixed nonce search."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-public8b-repeat-final-20261020';r.mkdir(exist_ok=True);s=(root/'experiments/autorun-20261020-breakthrough/finalize-exact154.py').read_text()
changes={'breakthrough-public140-exact154-nonce-20261020':'breakthrough-public8b-repeat-nonce-20261020','breakthrough-public140-exact154-20261020':'breakthrough-public8b-repeat-generic-20261020','breakthrough-public140-exact154-final-20261020':'breakthrough-public8b-repeat-final-20261020','breakthrough-public140-exact154-final-gate-20261020':'breakthrough-public8b-repeat-final-gate-20261020',"old/'SOURCE-FREEZE.json'":"old/'SOURCE-FREEZE-v2.json'",'6fddf1a9e7543416b123e2841f0fe94dc9600e91e985f9fd622516a354de5451':'a680f4d979df3ebdc5601616569705df1f115ebfcc059945d6c2cb3a183c53ab','7b165a67d95bdfadc274ddf303bf7a092c63d1d42bf223510e81d628be88fb3e':'4fb7a65acb7027fe9fa519b0db781f830c5cf1e1e5573afa102247401b3b6a01',"'submission_mode':'queue'":"'submission_mode':'auto'"}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
s=s.replace('Queue-only final rebuild','Automatic-submission research: final rebuild')
(r/'finalize.py').write_bytes(s.encode());(r/'.gitignore').write_bytes(b'/candidate/\n/target/\n/__pycache__/\n*resource-preflight*\n/point-add-source.tar.gz\n/evidence.tar.gz\n');(r/'.gitattributes').write_bytes(b'* -text\n*.tsv whitespace=-blank-at-eol\n')
subprocess.run(['ssh','smu_server','mkdir /home/hclau/ecdsa_research/breakthrough-public8b-repeat-final-20261020'],check=True);subprocess.run(['scp',str(r/'finalize.py'),'smu_server:/home/hclau/ecdsa_research/breakthrough-public8b-repeat-final-20261020/'],check=True)
subprocess.run(['ssh','smu_server','python3 /home/hclau/ecdsa_research/breakthrough-sparse-polynomial-20261020/launch-job.py breakthrough-public8b-repeat-final-20261020 finalize.py supervisor'],check=True)
