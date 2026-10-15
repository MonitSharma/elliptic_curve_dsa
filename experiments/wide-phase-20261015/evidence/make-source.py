"""Materialize a gate-inert source-location observer from the earlier workflow."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'phase-origin-20261015/prepare.py').read_text()
changes={"root.parent/'rail-control-20261015/square-room-b3'":"root.parent/'dynamic-pool-20261015/wide-b3'",'q.0==1191 && c.0==515 && self.ops.last().is_some_and(|op|op.kind==OperationType::CX && op.q_control1.0==1191 && op.q_target.0==207)':'q.0==221 && c.0==1566', '48e2f0d8ad9bdc492415ec2700fe5dda9edc0e6f1b3a21eb935ef61ecc3953a4':'95e771bae57bd96e75c11b569faf2f87cd7dfa52b227b40dd16e40a301d8e122','Must reproduce previous square-room stream exactly.':'Must reproduce the wide dynamic-pool stream exactly.'}
for a,b in changes.items():assert s.count(a)==1;(s:=s.replace(a,b))
(root/'prepare.py').write_text(s)
s=(root.parent/'carry-frame-20261015/run-origin.sh').read_text().replace('/carry-frame-20261015','/wide-phase-20261015').replace('prepare-origin.py','prepare.py').replace('/phase-origin-20261015/terminal-b3/ops.bin','/dynamic-pool-20261015/wide-b3/ops.bin')
(root/'run.sh').write_text(s,newline='\n')
