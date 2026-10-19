"""Compare coefficient growth under two exact integer choice rules.

This is a conjecture search. No observed maximum may become a circuit cut.
"""
import hashlib,json,math,statistics,time
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
from datetime import datetime,timezone
r=Path(__file__).resolve().parent
spec=spec_from_file_location('history',r.parent/'breakthrough-assessment-20261020/history-model.py');h=module_from_spec(spec);spec.loader.exec_module(h)
P=(1<<256)-(1<<32)-977
def choice(t,b,rule):
 if rule=='generic_full_compare':return h.bits_choice(t,b,abs(t)>4*abs(b))
 sign=((t>>1)^(b>>1))&1
 regular=(t+(1-2*sign)*b)//2
 other=t-(1-2*sign)*b
 v=10000 if other==0 else(abs(other)&-abs(other)).bit_length()-1
 if 2<=v<=4 and abs(other>>v)<abs(regular):
  return other>>v,sign^1,(v-1)&1,(v-1)>>1
 return regular,sign,0,0
def one(d,p,rule):
 a=d if d&1 else d-p;b=(a+(p if a%4==3 else-p))//2
 rr=[a,b];cc=[2,1];det=a-2*b;exponent=0;largest=2;peak=0
 for tick in range(4096):
  if abs(rr[0])==abs(rr[1]):
   assert abs(rr[0])==math.gcd(d,p)
   return {'ticks':tick,'cofactor_bits':largest.bit_length()+1,'cofactor_ratio':largest/p,'halvings':exponent,'combined':peak}
  ti=tick%2;si=1-ti;t,s0=h.forced(rr[ti],rr[si]);t,s1=h.forced(t,rr[si]);new,s3,k1,k2=choice(t,rr[si],rule)
  q=7-2*s0-4*s1-8*s3;e=3+k1+2*k2
  assert(rr[ti]+q*rr[si])==(new<<e)
  cc[ti]+=q*cc[si];cc[si]<<=e;rr[ti]=new;exponent+=e
  assert rr[0]*cc[1]-rr[1]*cc[0]==det
  largest=max(largest,*map(abs,cc));peak=max(peak,sum(abs(x).bit_length()+1 for x in rr+cc)+tick+5+exponent.bit_length())
 raise RuntimeError(('Diagnostic bound exceeded',d,p,rule))
def prime_below(bits):
 for p in range((1<<bits)-1,(1<<(bits-1)),-4):
  if all(p%d for d in range(3,math.isqrt(p)+1,2)):return p
 raise RuntimeError(bits)
def main():
 result={'status':'COFACTOR_BOUND_CONJECTURE_STUDY_NOT_A_PROOF_OR_CIRCUIT','label':'cofactor-growth-rule-comparison-v1','at_utc':datetime.now(timezone.utc).isoformat(),'small':{},'field':{},'no_empirical_allocation_cut':True}
 for rule in['generic_full_compare','minimum_absolute_next_target']:
  small=[]
  for n in range(5,16):
   p=prime_below(n);rows=[one(d,p,rule)for d in range(1,p)]
   record={'bits':n,'prime':p,'all_nonzero_inputs':len(rows),'max_cofactor_bits':max(x['cofactor_bits']for x in rows),'max_cofactor_ratio':max(x['cofactor_ratio']for x in rows),'max_halvings':max(x['halvings']for x in rows),'max_ticks':max(x['ticks']for x in rows)}
   small.append(record);print(rule,json.dumps(record),flush=True)
  result['small'][rule]=small
  rows=[]
  for i in range(4096):
   d=1+int.from_bytes(hashlib.shake_256(b'cofactor-growth-rule-comparison-v1'+i.to_bytes(8,'little')).digest(32),'little')%(P-1)
   rows.append(one(d,P,rule))
  result['field'][rule]={k:{'mean':statistics.mean(x[k]for x in rows),'max':max(x[k]for x in rows)}for k in rows[0]}
  (r/'BOUNDS-PROGRESS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
  print(rule,json.dumps(result['field'][rule]),flush=True)
 (r/'BOUNDS-STUDY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
