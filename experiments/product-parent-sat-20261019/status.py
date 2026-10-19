import json
from pathlib import Path
r=Path(__file__).resolve().parent
for name in ('SEEDED-RESULT.json','roots-lease-02-result.json','relations-02.json','graph-lease-02.progress.json','graph-lease-02-result.json'):
    p=r/name
    if not p.exists():continue
    d=json.loads(p.read_text())
    if name=='relations-02.json':
        out={k:d.get(k) for k in ('reference_count','unexpanded_definition_frontier','max_depth','global_definition_count')}
        out['definitions']=len(d['definitions']);out['roots']=len(d['root_atoms'])
    elif name=='roots-lease-02-result.json':
        out={k:d.get(k) for k in ('verdict','seconds')};out['boundary_atoms']=len(d['boundary_atoms'])
    else:out={k:v for k,v in d.items() if k not in ('global_properties','statistics','input','boundary_atoms')}
    print(name,json.dumps(out),flush=True)
for name in ('run','seeded','roots','relations'):
    p=r/(name+'.exit')
    if p.exists():print(name+'.exit',p.read_text().strip())
p=r.parent/'product-peak-synthesis-20261019/counted-prune.json'
if p.exists():
    d=json.loads(p.read_text());print('counted-prune',json.dumps({k:d[k] for k in ('recolored_physical_Q','provably_zero_identity_gates_removed','zero_identity_removed_by_kind','zero_Toffolis_always_executed','zero_Toffolis_conditionally_executed')}))
