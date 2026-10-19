import json
from pathlib import Path
r=Path(__file__).resolve().parent;e=r.parent;g=e/'product-guard-schedule-20261019'
assert (g/'run.exit').read_text().strip()=='0' and (g/'control.exit').read_text().strip()=='0'
assert json.loads((g/'CONTROL.json').read_text())['status']=='PROTECTED_SIMULATOR_MATERIALIZED_GUARD_PHYSICAL_TRANSCRIPT_CONTROL_PASS'
guard=json.loads((g/'scheduled.json').read_text())
cases=[]
for name,path,sha in [('public',e/'product-pareto-20261019/parent/ops.bin','429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842'),('guard',g/'scheduled.ordered.ops.bin',guard['output_full_sha3_256'])]:
    for gap in [1,64,4096]:cases.append({'name':f'{name}-{gap}','input':str(path),'input_sha3_256':sha,'gap':gap})
(r/'DECLARED-CASES.json').write_text(json.dumps(cases,indent=2)+'\n')
for x in cases:print('\t'.join(str(x[k]) for k in ['name','input','gap','input_sha3_256']))
