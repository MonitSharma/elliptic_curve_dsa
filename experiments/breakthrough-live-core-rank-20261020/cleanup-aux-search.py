"""Exact finite models for cheaper cleanup after 13 retained-form erasures."""
import json
from pathlib import Path
r=Path(__file__).resolve().parent
source=(r/'retained-cleanup.py').read_text();head=source[:source.index('while remaining:')];loop=source[source.index('while remaining:'):source.index('report=')]
initial=json.loads((r/'RETAINED-CLEANUP-MODEL.json').read_bytes())['unresolved'];order=['c1','c2','c3','r1','c4','c5','tt','r2','r3','y3','y4','y5'];out=[]
for count in range(1,len(order)+1):
 env={'__file__':str(r/'retained-cleanup.py')};exec(head,env);env['remaining']=[(n,env['f'][n])for n in initial+order[:count]];env['eliminated']=[];exec(loop,env)
 row={'added_aux':order[:count],'remaining':[n for n,v in env['remaining']],'erasure_order':[v['wire_function']for v in env['eliminated']],'phase_witnesses':env['eliminated']};out.append(row);print('aux',count,'remaining',row['remaining'],flush=True)
 if not row['remaining']:break
(r/'CLEANUP-AUX-SEARCH.json').write_text(json.dumps({'status':'EXACT_TRUTH_MODELS_ONLY','cases':out,'scope':'All16384 truth functions, Clifford phase repair elimination; auxiliary construction order, lifetime and full circuit implementation pending.'},indent=2)+'\n')
