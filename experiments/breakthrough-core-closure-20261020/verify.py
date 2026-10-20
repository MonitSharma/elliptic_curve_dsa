"""Independently evaluate every emitted XOR/AND witness on all native inputs."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;instance=json.loads((r/'INSTANCE-VERIFICATION.json').read_text());one=(1<<256)-1;results=[]
def expr(features,mask):
 out=one if mask>>63&1 else 0;mask&=(1<<63)-1
 assert mask>>len(features)==0
 for i,v in enumerate(features):
  if mask>>i&1:out^=v
 return out
for name in['control19','pure16']+[f'lift{i}'for i in range(1,7)]:
 p=r/(name+'.result.txt');lines=p.read_text().splitlines();features=[int(v,16)for v in instance['inputs']];metadata={};gates=[];outputs={}
 for line in lines:
  f=line.split()
  if f[0]=='GATE':
   index,a,b=map(int,f[1:4]);assert index==len(gates);value=sum(int(w)<<(64*j)for j,w in enumerate(f[4:]));assert value==(expr(features,a)&expr(features,b));features.append(value);gates.append({'a':a,'b':b,'truth':hex(value)})
  elif f[0]=='OUTPUT':outputs[int(f[1])]=int(f[2])
  else:metadata[f[0]]=f[1]
 assert int(metadata['GATES'])==len(gates)
 if metadata['STATUS']=='TARGET_REACHED':
  assert len(outputs)==len(instance['outputs']);assert all(expr(features,outputs[i])==int(v,16)for i,v in enumerate(instance['outputs']))
 results.append({'name':name,'metadata':metadata,'gates':gates,'output_forms':outputs,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert results[0]['metadata']['STATUS']=='TARGET_REACHED'and len(results[0]['gates'])<=19
(r/'MODEL-RESULT.json').write_text(json.dumps({'status':'ALL_EMITTED_WITNESSES_MATCH_ACTUAL_NATIVE_TRUTH','results':results,'instance_sha256':instance['instance_sha256'],'native_truth_sha256':instance['native_truth_sha256'],'scope':'Exact finite truth-function linear-product-closure model. CLOSED applies only to a fully enumerated specified allowed subspace; INCOMPLETE never proves absence. A pure-U closure below target excludes a16-AND Boolean XOR/AND straight-line network by rank, not general measured quantum circuits. Lift failures do not give universal17/18 bounds. No native point-add resource result, gate, nonce or novelty claim.'},indent=2)+'\n')
print(json.dumps([{'name':x['name'],'status':x['metadata']['STATUS'],'AND':len(x['gates'])}for x in results],indent=2))
