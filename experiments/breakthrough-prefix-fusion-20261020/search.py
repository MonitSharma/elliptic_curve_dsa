"""Monotone exact AND closure inside declared retained function spans."""
import hashlib,itertools,json,time
from pathlib import Path
r=Path(__file__).resolve().parent;d=json.loads((r/'PREFIX-DAG.json').read_bytes());f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];original=[one]+[f['input'+str(i)]for i in range(14)]
def comb(mask,cols):
 out=0
 while mask:
  bit=mask&-mask;out^=cols[bit.bit_length()-1];mask^=bit
 return out
for _,a,b in d['gates']:original.append(comb(a,original)&comb(b,original))
def add(basis,value,coef):
 while value:
  p=value.bit_length()-1
  if p not in basis:basis[p]=(value,coef);return None
  v,c=basis[p];value^=v;coef^=c
 return coef
def solve(basis,value):
 out=0
 while value:
  p=value.bit_length()-1
  if p not in basis:return None
  v,c=basis[p];value^=v;out^=c
 return out
reports=[]
for index,case in enumerate(json.loads((r/'INTERFACES.json').read_text())['cases']):
 started=time.time();cols=original[:15].copy();old_masks=[1<<i for i in range(15)];native_masks=old_masks.copy();steps=[];newgates=[];newhelpers=[];uforms=case['retained_helper_forms'];ufun=[comb(x,original)for x in uforms];tried=0;status='RESTRICTED_FACTOR_SEARCH_INCOMPLETE';base={}
 for i,x in enumerate(cols):add(base,x,1<<i)
 def keep(target,linear,aa,bb,origin):
  n=len(cols);av=comb(aa,cols);bv=comb(bb,cols);truth=comb(target,original);assert av&bv^comb(linear,cols)==truth and solve(base,truth)is None
  atom=1<<(15+len(steps));a=comb(aa,native_masks);b=comb(bb,native_masks);helper=atom^comb(linear,native_masks);newgates.append([64+len(steps),a,b]);newhelpers.append(helper);steps.append({'target_old_form':target,'linear':linear,'a':aa,'b':bb,'available_old_forms':old_masks.copy(),'origin':origin,'all16384_verified':True});cols.append(truth);old_masks.append(target);native_masks.append(helper);add(base,truth,1<<n)
 while len(steps)<30 and time.time()-started<120:
  progress=False
  for j,(_,a,b)in enumerate(d['gates']):
   if case['parity']>>j&1 or solve(base,original[15+j])is not None:continue
   ca=solve(base,comb(a,original));cb=solve(base,comb(b,original))
   if ca is not None and cb is not None:keep(1<<(15+j),0,ca,cb,'original_product');progress=True
  if progress:continue
  n=len(cols);candidates=[];seen=set()
  for _,a,b in d['gates']:
   for form in[a,b]:
    v=solve(base,comb(form,original))
    if v is not None and v&~1:candidates.append(v&~1)
  for weight in[1,2,3]:candidates.extend(sum(1<<i for i in ids)for ids in itertools.combinations(range(1,n),weight))
  hit=None
  for aa in candidates:
   if aa in seen:continue
   seen.add(aa);tried+=1;av=comb(aa,cols);basis=base.copy()
   for j,bv in enumerate(cols[1:],1):add(basis,av&bv,1<<(n+j))
   for j,truth in enumerate(ufun):
    relation=add(basis,truth,1<<(2*n+j))
    if relation is None:continue
    y=relation>>(2*n);linear=relation&((1<<n)-1);bb=relation>>n&((1<<n)-1)
    if not bb:continue
    target=comb(y,uforms)
    if solve(base,comb(target,original))is not None:continue
    assert comb(linear,cols)^(av&comb(bb,cols))==comb(target,original);hit=(target,linear,aa,bb);break
   if hit or time.time()-started>=120:break
  if hit:keep(*hit,'new_exact_factor')
  else:break
  print(json.dumps({'case':index,'ANDs':len(steps),'new_factor':hit[0],'seconds':time.time()-started}),flush=True)
 if len(steps)==30:
  newvalues=original[:15].copy()
  for _,a,b in newgates:newvalues.append(comb(a,newvalues)&comb(b,newvalues))
  def translated(mask):
   x=solve(base,comb(mask,original));assert x is not None;newmask=comb(x,native_masks);assert comb(newmask,newvalues)==comb(mask,original);return newmask
  result={'input_qubits':d['input_qubits'],'gates':newgates,'helper_masks':newhelpers,'field_masks':[translated(x)for x in d['field_masks']],'low_sum_masks':[translated(x)for x in d['low_sum_masks']],'c6_mask':translated(d['c6_mask']),'scope':'Exact30-AND active-prefix model; all14-input truth functions verified. Native phase/cleanup/workspace and complete resource tests pending.'};(r/'NEW-PREFIX-DAG.json').write_text(json.dumps(result,indent=2)+'\n');status='EXACT30_AND_DAG_ALL16384_VERIFIED_NOT_NATIVE'
 report={'case':case,'status':status,'ANDs_built':len(steps),'factor_candidates':tried,'seconds':time.time()-started,'steps':steps,'scope':'Original available products first, then sparse-weight<=3 or available original control form as left factor, arbitrary affine right factor/linear correction solved exactly by intersection with retained span. Monotone exact closure, finite restriction/time means failure is inconclusive. No packet data, native phase test or resource record.'};reports.append(report);(r/('case'+str(index)+'.json')).write_text(json.dumps(report,indent=2)+'\n');(r/'PROGRESS.json').write_text(json.dumps([{'case':i,'status':x['status'],'ANDs':x['ANDs_built']}for i,x in enumerate(reports)],indent=2)+'\n');print(index,status,len(steps),flush=True)
 if status.startswith('EXACT30'):break
(r/'RESULT.json').write_text(json.dumps({'status':'GLOBAL_PREFIX_FACTOR_CLOSURE_RESEARCH','cases':reports,'source_hashes':{p:hashlib.sha256((r/p).read_bytes()).hexdigest()for p in['search.py','PREFIX-DAG.json','FUNCTIONS.json','INTERFACES.json']}},indent=2)+'\n')
