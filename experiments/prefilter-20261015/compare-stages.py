import ast,json,re,sys
from pathlib import Path
import walk_model as m
root=Path(__file__).parent
rows=json.loads((root/'packets/audit-rows.json').read_text())
observed={}
for line in (root/'evidence/observer.log').read_text().splitlines():
    z=re.match(r'MODEL_OBS shot=(\d+) phase=(\w+) tick=(\d+) r0=(0x\w+) r1=(0x\w+) tape=(.*)',line)
    if not z:continue
    shot,phase,tick,a,b,tape=z.groups()
    observed[(int(shot),phase,int(tick))]=(int(a,16),int(b,16),ast.literal_eval(tape))
summaries=[];matches=0;total=0;bad=[]
standalone='--observed-seed' in sys.argv
for shot,row in enumerate(rows):
    tx,ty,ox,oy=[int(row[k],16) for k in ('tx','ty','ox','oy')]
    traces={}
    divide_seed=(2*observed[(shot,'divide',0)][1])%m.P if standalone else (tx-ox)%m.P
    tr=[];c,_,_=m.walk(divide_seed,trace=tr);traces['divide']=tr
    slope=c*((ty-oy)%m.P)%m.P
    after=(tx+2*ox-slope*slope)%m.P
    multiply_seed=(2*observed[(shot,'multiply',0)][1])%m.P if standalone else after
    tr=[];m.walk(multiply_seed,False,'multiply',trace=tr);traces['multiply']=tr
    first={};wrong=0;tapewrong=0
    for phase,tr in traces.items():
        for r in tr:
            got=observed.get((shot,phase,r['tick']))
            if got is None:continue
            expected=(r['r0'],r['r1'],r['tape'])
            ok=got==expected;matches+=ok;total+=1
            if not ok:
                wrong+=1;tapewrong+=got[2]!=expected[2]
                first.setdefault(phase,dict(tick=r['tick'],observed=got,model=expected))
    summaries.append(dict(shot=shot,batch=row['batch'],lane=row['lane'],value=int(row['value']),different_stages=wrong,different_tapes=tapewrong,first=first))
    if first:bad.append(shot)
report=dict(source='4b2ec52f',stream_gate_inert=True,observer_equal_protected_simulator=True,
            compared_stages=total,matching_stages=matches,shots=len(rows),shots_with_differences=bad,
            seed_policy='observed_each_leg_seed' if standalone else 'modeled_coordinate_propagation',
            status='DIAGNOSTIC_MODEL_PARTIAL_MATCH_NOT_CERTIFICATE',details=summaries)
name='stage-standalone.json' if standalone else 'stage-differential.json'
(root/'evidence'/name).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='details'}))
