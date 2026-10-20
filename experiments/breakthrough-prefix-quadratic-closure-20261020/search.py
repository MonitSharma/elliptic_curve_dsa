"""Necessary algebraic reachability filter; no circuit or resource score."""
import hashlib,itertools,json,time
from pathlib import Path
r=Path(__file__).resolve().parent
def comb(mask,cols):
 out=0
 while mask:
  bit=mask&-mask;out^=cols[bit.bit_length()-1];mask^=bit
 return out
def insert(basis,x):
 while x:
  p=x.bit_length()-1
  if p not in basis:basis[p]=x;return x
  x^=basis[p]
 return 0
def remainder(basis,x):
 while x:
  p=x.bit_length()-1
  if p not in basis:return x
  x^=basis[p]
 return 0
def closure(initial,universe,targets):
 ub={};bb={};cols=[]
 for x in universe:insert(ub,x)
 for x in initial:
  assert remainder(ub,x)==0
  v=insert(bb,x)
  if v:cols.append(v)
 history=[]
 while True:
  quotient={};new=[];n=len(cols);pairs=0
  for i,j in itertools.combinations(range(n),2):
   full=cols[i]&cols[j];projected=remainder_full(ub,full);pairs+=1
   while projected:
    p=projected.bit_length()-1
    if p not in quotient:quotient[p]=(projected,full);break
    q,y=quotient[p];projected^=q;full^=y
   if not projected:
    assert remainder(ub,full)==0
    v=insert(bb,full)
    if v:new.append(v)
  history.append({'rank_before':n,'quadratic_pairs':pairs,'outside_image_rank':len(quotient),'new_dimensions':len(new),'rank_after':len(bb)})
  cols.extend(new)
  if not new:break
 assert all(remainder(ub,x)==0 for x in cols)
 return {'rank':len(bb),'universe_rank':len(ub),'target_count':len(targets),'unreachable_target_indices':[i for i,x in enumerate(targets)if remainder(bb,x)],'history':history}
def remainder_full(basis,x):
 for p in sorted(basis,reverse=True):
  if x>>p&1:x^=basis[p]
 return x
def controls():
 one=(1<<8)-1;a=sum(1<<k for k in range(8)if k&1);b=sum(1<<k for k in range(8)if k&2);c=sum(1<<k for k in range(8)if k&4)
 # Sum of two unavailable products can be in U. A filter that discards each
 # product separately would incorrectly exclude this reachable sum.
 target=(a&b)^(a&c);v=closure([one,a,b,c],[one,a,b,c,target],[target]);assert v['rank']==5 and not v['unreachable_target_indices']
 cubic=a&b&c;v=closure([one,a,b,c],[one,a,b,c,cubic],[cubic]);assert v['rank']==4 and v['unreachable_target_indices']==[0]
 v=closure([one,a,b,c],[one,a,b,c,a&b,cubic],[cubic]);assert v['rank']==6 and not v['unreachable_target_indices']
 return 3
if __name__=='__main__':
 controls_passed=controls();start=time.time();d=json.loads((r/'PREFIX-DAG.json').read_text());f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_text()).items()};original=[f['one']]+[f['input'+str(i)]for i in range(14)]
 for _,a,b in d['gates']:original.append(comb(a,original)&comb(b,original))
 basis={}
 for x in original:insert(basis,x)
 assert len(basis)==46
 required=d['field_masks']+d['low_sum_masks']+[d['c6_mask']];targets=[comb(x,original)for x in required];reports=[]
 for i,case in enumerate(json.loads((r/'INTERFACES.json').read_text())['cases']):
  universe=original[:15]+[comb(x,original)for x in case['retained_helper_forms']];ans=closure(original[:15],universe,targets);ans['case']=i;ans['parity']=case['parity'];reports.append(ans);print(json.dumps(ans),flush=True)
 result={'status':'ALGEBRAIC_NECESSARY_FILTER_NOT_CIRCUIT_OR_SCORE','controls_passed':controls_passed,'cases':reports,'cases_excluding_required_output':sum(bool(x['unreachable_target_indices'])for x in reports),'cases_with_no_obstruction':sum(not x['unreachable_target_indices']for x in reports),'seconds':time.time()-start,'source_hashes':{p:hashlib.sha256((r/p).read_bytes()).hexdigest()for p in['search.py','PREFIX-DAG.json','FUNCTIONS.json','INTERFACES.json']},'scope':'Fixed-point B <- span(B, span(pairwise products of B) intersect U), exact truth functions on all 16384 inputs. This deliberately overapproximates sequential AND reachability: added intersections can require multiple products. Missing required output excludes circuits whose EVERY intermediate truth function lies in that U; containing outputs supplies no construction. All63 codimension-one U containing required outputs within the original46-dimensional function span. No unrestricted AND/Toffoli/quantum lower bound and no resource result.'};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='cases'}),flush=True)
