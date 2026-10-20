"""Hold reconstruction auxiliaries until every original retained form clears."""
import json
from pathlib import Path
r=Path(__file__).resolve().parent
source=(r/'retained-cleanup.py').read_text();head=source[:source.index('while remaining:')];loop=source[source.index('while remaining:'):source.index('report=')]
loop=loop.replace('for name,g in reversed(remaining):','for name,g in ([(n,v)for n,v in remaining if n in initial] if any(n in initial for n,v in remaining) else list(reversed(remaining))):')
initial=json.loads((r/'RETAINED-CLEANUP-MODEL.json').read_bytes())['unresolved'];order=['c1','c2','c3','r1','c4','c5','tt','r2','r3','y3','y4','y5'];out=[]
for count in range(1,len(order)+1):
 env={'__file__':str(r/'retained-cleanup.py'),'initial':initial};exec(head,env);env['remaining']=[(n,env['f'][n])for n in initial+order[:count]];env['eliminated']=[];exec(loop,env)
 row={'added_aux':order[:count],'remaining':[n for n,v in env['remaining']],'erasure_order':[v['wire_function']for v in env['eliminated']],'phase_witnesses':env['eliminated']};out.append(row);print('aux',count,'remaining',row['remaining'],flush=True)
 if not row['remaining']:break
(r/'CLEANUP-AUX-HELD-SEARCH.json').write_text(json.dumps({'status':'EXACT_TRUTH_MODELS_ONLY','cases':out,'scope':'All16384 truth functions, retain aux while clearing original7 forms; native construction and lifecycle pending.'},indent=2)+'\n')
