"""Construct fixed structured capacity regressions by reversing Euclid.

These are field-denominator fixtures, never hash-derived benchmark packets.
The ideal screen omits source envelopes, real carry errors and quantum phase.
"""
import collections,hashlib,importlib.util,json,math,random
from pathlib import Path
root=Path(__file__).resolve().parents[1];p=root/'experiments/overnight-20261014/qubits/qubit-screen-n274.py'
spec=importlib.util.spec_from_file_location('m',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[list(map(int,l.split()[1:]))for l in(root/'agents/qubits/src/point_add/sched_frogdrop.txt').read_text().splitlines()if l.startswith('C ')]
rng=random.Random(0xecd5a2320261014);found=[]
for attempt in range(256):
 tc=rng.randrange(1<<109,1<<110)|1;tp=rng.randrange(1,tc)
 if math.gcd(tc,tp)!=1:continue
 target=m.P//tc//5000000;rc=m.P*pow(tp,-1,tc)%tc;rc+=max(0,(target-rc)//tc)*tc
 rp=(m.P-rc*tp)//tc
 if rc<=0 or rp<=rc:continue
 q=rp//rc
 if not(1<<22<=q<1<<23):continue
 a,b,aa,bb=tc,tp,rp,rc
 while b:
  k,rem=divmod(a,b);aa,bb=bb+k*aa,aa;a,b=b,rem
 assert a==1 and aa==m.P and 0<bb<m.P
 pub=m.screen(bb,rows,collections.Counter(),small_cutoff=0,small_head=24,large_head=24,mixed_cap=23,pure_cap=23,reserve=7)
 new=m.screen(bb,rows,collections.Counter(),small_cutoff=96,small_head=32,large_head=24,mixed_cap=22,pure_cap=24,reserve=9)
 extra=[e for e in new if e['kind']=='quotient_cap'and e['q']==q]
 if extra:
  found.append({'attempt':attempt,'input':hex(bb),'tcur':hex(tc),'tprev':hex(tp),'rprev':hex(rp),'rcur':hex(rc),'q':q,'public_model_events':pub,'n275_model_events':new})
  if len(found)==4:break
out={'status':'STRUCTURED_IDEAL_MODEL_COUNTEREXAMPLES_ONLY','qualified_score':None,'seed':'0xecd5a2320261014','method':'Choose coprime110bit coefficient pair; solve P=rprev*tcur+rcur*tprev then reverse coefficient Euclid to recover field denominator. Fixed targetq5000000. No nonce/packet search.','fixtures':found,'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'limits':'Model ignores source envelopes, real carries/phase. These are local arithmetic-model capacity counterexamples, not yet admitted full-source counterexamples.'}
(root/'research-output/overnight-20261014/mixedhr23-structured-model.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'fixtures':len(found),'first':found[:1]}))
