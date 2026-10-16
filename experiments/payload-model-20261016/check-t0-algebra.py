"""Source-derived integer fold of P3_T0_ONE_ADD versus generic three-add.
This tests a primitive contract, not candidate circuits, packets or nonces.
"""
from pathlib import Path
import json,random
import walk_model as m
mask=(1<<256)-1;f=(1<<32)+977
def fold(X,Nm,extra,w=57):
 s=3+extra;E=X>>256;L=X&mask;A=L+E+(E-Nm)*(f-1);digit=A*pow(f,-1,1<<s)&((1<<s)-1);C=E+(E-Nm-digit)*(f-1);W=(L&~((1<<w)-1))+((L+C)&((1<<w)-1));return ((W>>s)+digit*(1<<(256-s)))%m.P
def oneadd(T,S,signs,extra):
 n0,n1,n2=signs;a0=n2&(1-n1);a1=a0&n0;j=1 if n1 else 0 if a0 else 2;sc=n0^a0;tc=n2^a0^a1
 X=((mask-T if tc else T)<<j)+(mask-S if sc else S);Nm=sc+(tc<<j);return fold(X,Nm,extra)
def main():
 rng=random.Random(11016);values=[0,1,m.P-1]
 for i in range(256):values.extend([1<<i,((1<<i)-1)%m.P])
 for k in range(1,9):
  for j in range(1,10):
   for e in range(0,42,3):
    for sg in [-1,0,1]:values.append(((k<<57)//j+sg*(1<<e))%m.P)
 values.extend(rng.randrange(m.P)for _ in range(20000));found=[];checked=0
 for T in values:
  S=m.half(T)
  for signs in [(n&1,(n>>1)&1,(n>>2)&1)for n in range(8)]:
   for extra in range(4):
    generic=m.onefold(T,S,signs,extra,0);actual=oneadd(T,S,signs,extra);checked+=1
    if generic!=actual:
     found.append(dict(T=T,S=S,signs=signs,extra=extra,generic=generic,oneadd=actual,delta=(actual-generic)%m.P))
     if len(found)>=16:break
   if len(found)>=16:break
  if len(found)>=16:break
 result=dict(checked=checked,mismatches=found,status='INTEGER_ALGEBRA_COUNTEREXAMPLE_NOT_YET_PROTECTED_GATE_REPLAY')
 Path(__file__).with_name('t0-algebra.json').write_text(json.dumps(result,indent=2)+'\n');print('checked',checked,'counterexamples',len(found));print(found[:2])
if __name__=='__main__':main()
