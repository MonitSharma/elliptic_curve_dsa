"""Exact signed-fold algebra on real observed transition witnesses."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parent
text=(root/'evidence/generate.log').read_text()
P=2**256-2**32-977;F=2**32+977;mask=2**256-1
rows=[]
for line in text.splitlines():
 if not line.startswith('PAY_EVENT family=floor31 '):continue
 v=dict(re.findall(r'(\w+)=([^ ]+)',line));tape=json.loads(re.search(r'tape=(\[[^]]+\])',line)[1]);assert len(tape)==5
 a,b=int(v['a'],16),int(v['b'],16);extra=tape[3]+2*tape[4];shift=3+extra;tick=int(v['tick']);rev=v['rev']=='true';w=57 if not rev and (tick<=55 or tick==104) else 56
 if not rev:
  nm=sum(si<<i for i,si in enumerate(tape[:3]));X=a+sum((b if si==0 else mask-b)<<i for i,si in enumerate(tape[:3]));E=X>>256;L=X&mask
  A=L+E+(E-nm)*(F-1);d=2**shift;m=(A*pow(F,-1,d))%d;C=E+(E-nm-m)*(F-1);c=((L%(2**w))+C)//2**w
  W=A-m*(F-1);assert W%d==m
  exact=(W//d+m*2**(256-shift))%P
  window=(L-L%(2**w))+((L%(2**w)+C)%2**w)
  wrong=(window//d+m*2**(256-shift))%P
  correction=c*2**(w-shift)
 else:
  W=((a<<shift)&mask)|(a>>(256-shift));flipped=[1-si for si in tape[:3]];nm=sum(si<<i for i,si in enumerate(flipped))
  X=W+sum((b if si==0 else mask-b)<<i for i,si in enumerate(flipped));E=X>>256;L=X&mask;m=W%(2**shift)
  C=E+(E-nm+m)*(F-1);c=((L%(2**w))+C)//2**w
  exact=(L+C)%P;wrong=((L-L%(2**w))+((L%(2**w)+C)%2**w))%P;correction=c*2**w
 assert exact==int(v['want_t'],16),(tick,hex(exact),v['want_t'])
 assert wrong==int(v['got_t'],16),(tick,hex(wrong),v['got_t'])
 assert (wrong+correction)%P==exact
 rows.append({'shot':int(v['shot']),'tick':tick,'reverse':rev,'window':w,'shift':shift,'nm':nm,'E':E,'m':m,'C':C,'low_L':L%(2**w),'signed_boundary_c':c,'signed_correction':correction,'matches_observed_got_and_want':True})
out={'qualified_score':None,'cases':rows,'all_match':all(r['matches_observed_got_and_want'] for r in rows),'internal_wire_observation':False,'description':'Reconstructed from observed whole-tick entry payload and live tape, not direct fold wires.'}
(root/'boundary-reconstruction.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
