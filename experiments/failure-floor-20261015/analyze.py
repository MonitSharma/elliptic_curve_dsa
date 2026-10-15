"""Parse completed observer evidence; reject incomplete or false-control traces."""
from pathlib import Path
import re,json,collections,hashlib
root=Path(__file__).resolve().parent
log=root/'evidence/generate.log'
text=log.read_text()
manifest=json.loads((root/'evidence/manifest.json').read_text())
events=[]
for line in text.splitlines():
 if not line.startswith('PAY_EVENT '):continue
 vals=dict(re.findall(r'(\w+)=([^ ]+)',line))
 tape=json.loads(re.search(r'tape=(\[[^]]+\])',line)[1])
 for k in ['shot','at','tick']:vals[k]=int(vals[k])
 for k in ['a','b','got_t','want_t','got_s','want_s','diff']:vals[k]=int(vals[k],16)
 vals['tape']=tape;vals['coefficient']=sum((1-2*v)*(1<<i) for i,v in enumerate(tape[:-2]))
 vals['shift']=len(tape)-2+(0 if vals['skip']=='true' else tape[-2]+2*tape[-1])
 if vals['family']=='floor31':vals['parent_shot']=manifest['floor_parent_shots'][vals['shot']]
 p=2**256-2**32-977;d=vals['diff'];sgn=d if d<p//2 else d-p
 vals['signed_delta']=sgn;mag=abs(sgn);vals['delta_power']=mag.bit_length()-1 if mag and not mag&(mag-1) else None
 events.append(vals)
summaries=[dict(re.findall(r'(\w+)=([^ ]+)',l)) for l in text.splitlines() if l.startswith('PAY_SUMMARY ')]
assert len(summaries)==2,summaries
assert all(s['observer_equal']=='true' for s in summaries)
ind=next(s for s in summaries if s['family']=='independent');assert ind['final_bad']=='0' and ind['first_events']=='0',ind
floor=next(s for s in summaries if s['family']=='floor31');assert floor['shots']=='31' and floor['final_bad']=='31',floor
out={'qualified_score':None,'summaries':summaries,'events':events,'first_event_groups':dict(collections.Counter(f"{e['phase']}:{e['rev']}:{e['tick']}" for e in events)),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
(root/'result.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='events'},indent=2))
