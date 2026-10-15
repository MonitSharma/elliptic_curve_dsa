import json,re
from pathlib import Path
import walk_model as m
root=Path(__file__).parent
rows=json.loads((root/'packets/audit-rows.json').read_text());forward={};reverse={}
for line in (root/'evidence/observer-reverse.log').read_text().splitlines():
    z=re.match(r'MODEL_(OBS|REV) shot=(\d+) phase=(\w+) tick=(\d+) r0=(0x\w+) r1=(0x\w+)',line)
    if z:
        kind,shot,phase,tick,a,b=z.groups();(forward if kind=='OBS' else reverse)[int(shot),phase,int(tick)]=(int(a,16),int(b,16))
total=matches=0;details=[]
for shot,row in enumerate(rows):
    first={};wrong=0
    for phase in ('divide','multiply'):
        d=2*forward[shot,phase,0][1]%m.P
        trace=[];m.walk(d,phase=='divide',phase,reverse_trace=trace)
        for t in trace:
            actual=reverse.get((shot,phase,t['tick']))
            if actual is None:continue
            expected=t['r0'],t['r1'];total+=1;matches+=actual==expected
            if actual!=expected:
                wrong+=1;first.setdefault(phase,dict(tick=t['tick'],actual=actual,model=expected))
    details.append(dict(shot=shot,value=int(row['value']),different_stages=wrong,first=first))
result=dict(source='4b2ec52f',shots=len(rows),compared_stages=total,matching_stages=matches,
            shots_with_differences=[r['shot']for r in details if r['first']],details=details,
            status='DIAGNOSTIC_REVERSE_MODEL_NOT_CERTIFICATE')
(root/'evidence/reverse-stage-differential.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='details'}))
