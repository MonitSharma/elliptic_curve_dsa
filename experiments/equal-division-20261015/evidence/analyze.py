"""Exact field checks for fixed no-held-flag division and observed payload ticks."""
from pathlib import Path
import re,json,sys
root=Path(__file__).resolve().parent;mode=sys.argv[1] if len(sys.argv)>1 else 'observer';assert mode in ['observer','fold'];text=(root/(mode+'.log')).read_text();p=2**256-2**32-977
inputs={m[0]:{'x':int(m[1],16),'y':int(m[2],16)} for m in re.findall(r'DIVISION_INPUT case=(\w+) x=(0x[0-9a-f]+) y=(0x[0-9a-f]+)',text)}
results=[]
for case,x,y,phase in re.findall(r'DIVISION_OUTPUT case=(\w+) x=(0x[0-9a-f]+) y=(0x[0-9a-f]+) phase=(0x[0-9a-f]+)',text):
 inp=inputs[case];expected=inp['y']*pow(inp['x'],-1,p)%p
 results.append({'case':case,'input_x':hex(inp['x']),'input_y':hex(inp['y']),'output_x':x,'output_y':y,'expected_y':hex(expected),'x_restored':int(x,16)==inp['x'],'correct_mod_p':int(y,16)%p==expected,'phase':phase})
assert len(results)==4
ticks={}
for label,t,op,a,b,letter in re.findall(r'DIVISION_TICK label=(\w+) tick=(\d+) op=(\d+) cond=0x[0-9a-f]+ a=(0x[0-9a-f]+) b=(0x[0-9a-f]+) letter=\[([^\]]*)\]',text):
 ticks.setdefault(int(t),{})[label]={'op':int(op),'a':int(a,16),'b':int(b,16),'letter':list(map(int,letter.split(', '))) if letter else []}
checks=[]
for t,pair in sorted(ticks.items()):
 if not {'before','after'}<=pair.keys():continue
 a=pair['before'];b=pair['after'];letter=b['letter'];assert len(letter)==5
 coefficient=sum((1-2*letter[i])*(1<<i) for i in range(3));shift=3+letter[3]+2*letter[4]
 expected=(a['a']+coefficient*a['b'])*pow(pow(2,shift,p),-1,p)%p
 checks.append({'tick':t,'before_op':a['op'],'after_op':b['op'],'coefficient':coefficient,'shift':shift,'before_target':hex(a['a']),'source':hex(a['b']),'actual_target':hex(b['a']),'expected_target':hex(expected),'correct':b['a']%p==expected,'source_unchanged':a['b']==b['b'],'delta_mod_p':hex((b['a']-expected)%p)})
result={'score':None,'status':'fixed correlated-input arithmetic probe','division_results':results,'tick_checks':checks,'first_tick_divergence':next((r for r in checks if not r['correct'] or not r['source_unchanged']),None),'limitations':['One preserved denominator and four predeclared payload values.','All-zero measurements only; no phase proof.','Injected arithmetic inputs are component tests, not full on-curve point-addition inputs.','Tick checks cover ordinary loops before the N2 batch; hidden substeps require follow-up observation.','Raw pre-Y33 stream; protected simulator agreement does not imply final candidate qualification.']}
(root/(mode+'-analysis.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'results':results,'ticks_checked':len(checks),'first_divergence':result['first_tick_divergence']},indent=2))
