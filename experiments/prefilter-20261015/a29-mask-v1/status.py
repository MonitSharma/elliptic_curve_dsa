from pathlib import Path
import json
p=Path(__file__).resolve().parent
for name in ['global','map-v2','scan']:
 q=p/(name+'.exit')
 print(name, q.read_text().strip() if q.exists() else 'ACTIVE_OR_NOT_STARTED')
q=p/'global.log'
if q.exists():
 lines=q.read_text().splitlines()
 print('last',lines[-1][:240] if lines else '')
 shadows=[json.loads(l.split(' ',1)[1]) for l in lines if l.startswith('APPLIED_SHADOW_CONTRACT ')]
 print('shadows',len(shadows),'last',[(x['start'],x['end_exclusive']) for x in shadows[-3:]])
 print('progress',[l for l in lines if l.startswith('GLOBAL_RNG_PROGRESS')][-2:])
q=p/'global.json'
if q.exists() and q.stat().st_size:
 d=json.loads(q.read_text())
 print({k:d[k] for k in ['mask_nodes','certified_reset_regions','input_only_dag_nodes','rng_draws','unresolved_rng_dependent_bits','concrete_known_output_bits','concrete_certified_wrong_shots','seconds']})
