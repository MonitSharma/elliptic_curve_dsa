import json,os,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;rows=[]
for name in ['c1','c2','c3','c4','tt','r2','r3','y3','y4','c5','y5']:
 env=dict(os.environ,PREFIX_BASIS_STRATEGY='original-forward',PREFIX_ERASE_STRATEGY='minimum',PREFIX_PROTECT=name);p=subprocess.run([sys.executable,str(r/'protected-schedule-model.py')],env=env,stdout=subprocess.PIPE,check=True);row=json.loads(p.stdout);rows.append(row);print(json.dumps({k:row[k]for k in ['protected_function','greedy_quadratic_erasure_helper_peak','quadratic_only_final_helpers','final_helpers_after_cubic_attempt','finishing_cubic_terms']}),flush=True)
(r/'PROTECTED-GRID.json').write_bytes((json.dumps({'status':'FINITE_PROTECTED_FUNCTION_MODEL_ONLY','cases':rows,'scope':'Native synthesis and full circuit integration pending; no score.'},indent=2)+'\n').encode())
