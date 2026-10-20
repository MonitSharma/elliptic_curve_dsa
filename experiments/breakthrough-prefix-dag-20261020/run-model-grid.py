import itertools,json,os,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;rows=[]
for basis,erase in itertools.product(['previous','original-forward','original-reverse'],['minimum','forward','reverse']):
 env=dict(os.environ,PREFIX_BASIS_STRATEGY=basis,PREFIX_ERASE_STRATEGY=erase);p=subprocess.run([sys.executable,str(r/'schedule-model.py')],env=env,check=True,stdout=subprocess.PIPE);row=json.loads(p.stdout);rows.append(row);print(json.dumps({k:row[k]for k in ['basis_strategy','erase_strategy','greedy_quadratic_erasure_helper_peak','quadratic_only_final_helpers','final_helpers_after_cubic_attempt','finishing_cubic_terms']}),flush=True)
(r/'MODEL-GRID.json').write_bytes((json.dumps({'status':'FINITE_GREEDY_MODEL_GRID_ONLY','cases':rows,'scope':'No native basis scheduling, component resource gain or full-circuit result.'},indent=2)+'\n').encode())
