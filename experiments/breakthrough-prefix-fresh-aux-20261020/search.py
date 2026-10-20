"""Find interfaces that survive the exact necessary closure with one new quadratic."""
import hashlib,itertools,json,time
from pathlib import Path
import closure_engine as e
r=Path(__file__).resolve().parent;started=time.time();assert e.controls()==3
d=json.loads((r/'PREFIX-DAG.json').read_text());f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_text()).items()};original=[f['one']]+[f['input'+str(i)]for i in range(14)]
for _,a,b in d['gates']:original.append(e.comb(a,original)&e.comb(b,original))
ob={}
for x in original:e.insert(ob,x)
assert len(ob)==46
targets=[e.comb(x,original)for x in d['field_masks']+d['low_sum_masks']+[d['c6_mask']]];parities=[x['parity']for x in json.loads((r/'INTERFACES.json').read_text())['cases']];assert len(parities)==63
planes=set()
for a,b in itertools.combinations(parities,2):planes.add(tuple(sorted((a,b,a^b))))
assert len(planes)==651
interfaces=[]
for a,b,_ in sorted(planes,key=lambda p:(sum(x.bit_count()for x in p),p)):
 constraints={}
 for row in[a,b]:e.insert(constraints,row)
 forms=[]
 for q in range(31):
  if q in constraints:continue
  x=1<<q
  for pivot in sorted(constraints):
   if(constraints[pivot]&x).bit_count()%2:x|=1<<pivot
  assert (x&a).bit_count()%2==(x&b).bit_count()%2==0;forms.append(x<<15)
 assert len(forms)==29;interfaces.append({'constraints':[a,b],'retained_helper_forms':forms})
aux=[]
for a,b in itertools.combinations(range(1,15),2):
 truth=original[a]&original[b]
 if e.remainder(ob,truth):aux.append({'input_columns':[a,b],'truth':truth})
assert aux
(r/'DECLARATION.json').write_text(json.dumps({'cases':len(aux),'interfaces_per_case':651,'choice':'All unordered distinct pairs of14 primary inputs, exclude products already in original46-dimensional span. Independent of curve/census/nonce data.','source_hashes':{p:hashlib.sha256((r/p).read_bytes()).hexdigest()for p in['search.py','closure_engine.py','FUNCTIONS.json','PREFIX-DAG.json','INTERFACES.json']},'scope':'Necessary overapproximation only. One fresh quadratic counted as1 AND; remaining<=29 functions confined to original span plus that auxiliary. Search all codimension-two original-helper interfaces containing outputs, with auxiliary supplied to the closure. Stop on first surviving interface; survival is not a circuit or feasibility proof.'},indent=2)+'\n')
reports=[];survivor=None
for k,case in enumerate(aux):
 t=time.time();ranks={};tested=0
 for index,interface in enumerate(interfaces):
  universe=original[:15]+[case['truth']]+[e.comb(x,original)for x in interface['retained_helper_forms']];ans=e.closure(original[:15]+[case['truth']],universe,targets);tested+=1;ranks[str(ans['rank'])]=ranks.get(str(ans['rank']),0)+1
  if not ans['unreachable_target_indices']:
   survivor={'auxiliary':case['input_columns'],'auxiliary_truth_hex':hex(case['truth']),'interface_index':index,**interface,'closure':ans,'scope':'Survives necessary overapproximation; no exact factorization/native circuit or resource score.'};(r/'SURVIVOR.json').write_text(json.dumps(survivor,indent=2)+'\n');break
 report={'auxiliary':case['input_columns'],'interfaces_tested':tested,'closure_rank_histogram':ranks,'seconds':time.time()-t,'survivor':survivor is not None};reports.append(report);print(json.dumps(report),flush=True);(r/'PROGRESS.json').write_text(json.dumps(reports,indent=2)+'\n')
 if survivor:break
(r/'RESULT.json').write_text(json.dumps({'status':'NECESSARY_FILTER_SURVIVOR_NOT_CIRCUIT'if survivor else'FIXED_RAW_INPUT_QUADRATIC_AUXILIARIES_EXCLUDED_WITHIN_DECLARED_SPAN','cases':reports,'declared_auxiliaries':len(aux),'survivor':survivor,'seconds':time.time()-started,'scope':'Exact full14-input truth-function closure, deliberately overapproximate. Negative applies only to the declared one-fresh-primary-pair auxiliary and original-span-plus-auxiliary language. No unrestricted AND/Toffoli lower bound; positive supplies no sequential program.'},indent=2)+'\n')
