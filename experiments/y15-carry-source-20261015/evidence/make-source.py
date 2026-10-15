"""Materialize a gate-inert observer of the remaining wide phase witness."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'wide-phase-20261015/prepare.py').read_text()
changes={"dynamic-pool-20261015/wide-b3":"y15-unseeded-20261015/wide-b3",'q.0==221 && c.0==1566':'q.0==135 && c.0==1555','95e771bae57bd96e75c11b569faf2f87cd7dfa52b227b40dd16e40a301d8e122':'0e5b5f6f2640da7e50c6bb0ae788f093d4df7fedba811007b6a2894879dd6b3e','wide dynamic-pool stream':'wide Y15 seedless stream'}
for a,b in changes.items():assert s.count(a)==1;s=s.replace(a,b)
(root/'prepare.py').write_text(s)
s=(root.parent/'wide-phase-20261015/run.sh').read_text().replace('/wide-phase-20261015','/y15-carry-source-20261015').replace('/dynamic-pool-20261015/wide-b3/ops.bin','/y15-unseeded-20261015/wide-b3/ops.bin')
(root/'run.sh').write_text(s,newline='\n')
(root/'collect.py').write_text((root.parent/'wide-phase-20261015/collect.py').read_text())
(root/'verify-local.py').write_text((root.parent/'wide-phase-20261015/verify-local.py').read_text())
