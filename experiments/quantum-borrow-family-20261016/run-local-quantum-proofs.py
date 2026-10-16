from pathlib import Path
import json,subprocess
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016');binary=r.parent/'seam-phase-repair-20261016/tool/target/release/quantum_phase'
for s in json.loads((r/'flag-regions.json').read_text()):
 j=s['site'];lower=','.join(map(str,s['lower']))
 for mode in ['old','new','negative']:
  args=[str(binary),str(r/f'{mode}-flag-{j}.bin'),'0']+([]if mode=='old'else[lower])
  with(r/f'{mode}-quantum-contract-{j}.json').open('w')as out,(r/f'{mode}-quantum-contract-{j}.log').open('w')as err:p=subprocess.run(args,stdout=out,stderr=err)
  (r/f'{mode}-quantum-contract-{j}.exit').write_text(str(p.returncode)+'\n')
  if mode=='negative':assert p.returncode!=0,('negative phase mutation was not rejected',j)
  else:
   assert p.returncode==0,(j,mode,p.returncode)
   x=json.loads((r/f'{mode}-quantum-contract-{j}.json').read_text());assert x['phase_contract_proved']and not x['q_contract_unresolved']and x['outer_caps']==0 and x['mr']==2*s['k']-1+(mode=='new')
 print('LOCAL_PROOF',j,'old/new exact with all MR and negative rejected',flush=True)
