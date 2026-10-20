"""Emit source-derived reversible basis change and exact phase certificates."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-live-core-rank-20261020';f={k:int(v,16)for k,v in json.loads((old/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];names=list(f)[15:46];assert len(names)==31 and names[-1]=='program13'
low=[f['input0']^f['input6'],f['input1']^f['input7']^f['c1'],f['input2']^f['input8']^f['c2'],f['input3']^f['c3'],f['input4']^f['c4']^f['k0'],f['input5']^f['c5']^f['k0']^f['k1']]
original=[one]+[f[f'input{i}']for i in range(6,14)]+low+[f[n]for n in names];basis={}
for i,v in enumerate(original):
 coef=1<<i
 while v:
  h=v.bit_length()-1
  if h not in basis:basis[h]=(v,coef);break
  w,c=basis[h];v^=w;coef^=c
 assert v
def coords(v):
 coef=0
 while v:
  h=v.bit_length()-1;w,c=basis[h];v^=w;coef^=c
 return coef
phase=json.loads((old/'QUADRATIC-LOAN-REVERSE-MODEL.json').read_bytes());factor=json.loads((old/'SPARSE-REBUILD.json').read_bytes());newnames=phase['selected_output_basis']+phase['garbage_basis'];assert len(newnames)==31
rows=[coords(f[n])for n in newnames];mat=[v>>15 for v in rows];ops=[]
def rowxor(a,b):mat[b]^=mat[a];ops.append((a,b))
for i in range(31):
 pivot=next(j for j in range(i,31)if mat[j]>>i&1)
 if pivot!=i:rowxor(i,pivot);rowxor(pivot,i);rowxor(i,pivot)
 for j in range(31):
  if i!=j and mat[j]>>i&1:rowxor(i,j)
assert mat==[1<<i for i in range(31)]
forward=list(reversed(ops));offsets=[v&((1<<15)-1)for v in rows]
feature={'one':0,**{f'input{i}':i-5 for i in range(6,14)},**{f'sum{i}':9+i for i in range(6)},**{n:15+i for i,n in enumerate(newnames)}}
def mask(ns):
 v=0
 for n in ns:v^=1<<feature[n]
 return v
cpp=[];cpp.append('const CORE_LOAN_BASIS_CX:&[(usize,usize)]=&'+repr(forward).replace('[','[').replace(']',']')+';')
cpp.append('const CORE_LOAN_OFFSETS:&[u64]=&['+','.join(hex(x)for x in offsets)+'];')
cpp.append('const CORE_LOAN_ERASE:&[(usize,&[(usize,usize)])]=&[')
for item in phase['quadratic_phase_eliminations']:
 terms=[(feature[t[0]],feature[t[1]]if len(t)==2 else 0)for t in item['phase_terms']]
 cpp.append('('+str(newnames.index(item['wire_function']))+',&['+','.join(f'({a},{b})'for a,b in terms)+']),')
cpp.append('];')
cpp.append('const CORE_LOAN_REBUILD:&[(usize,u64,&[(u64,u64)])]=&[')
for item in reversed(factor['witnesses']):
 cpp.append('('+str(newnames.index(item['wire_function']))+','+hex(mask(item['linear']))+',&['+','.join(f'({hex(mask(a))},{hex(mask(b))})'for a,b in item['products'])+']),')
cpp.append('];')
(r/'certificate-sparse.rs').write_bytes(('\n'.join(cpp)+'\n').encode())
(r/'MODEL-CERTIFICATE-SPARSE.json').write_text(json.dumps({'status':'ALL_TRUTH_IDENTITIES_VERIFIED_MODEL_ONLY','source_functions_sha256':hashlib.sha256((old/'FUNCTIONS.json').read_bytes()).hexdigest(),'phase_witness_sha256':hashlib.sha256((old/'QUADRATIC-LOAN-REVERSE-MODEL.json').read_bytes()).hexdigest(),'factor_witness_sha256':hashlib.sha256((old/'SPARSE-REBUILD.json').read_bytes()).hexdigest(),'certificate_sha256':hashlib.sha256((r/'certificate-sparse.rs').read_bytes()).hexdigest(),'old_helper_names':names,'new_helper_basis_names':newnames,'linear_transform_cnot_count':len(ops),'erased_helpers':11,'retained_helpers':20,'reconstruction_ANDs':11,'scope':'Independent native circuit tests pending. No whole point-add resource result.'},indent=2)+'\n');print('certificate',len(ops),'CX;',11,'erased;',11,'reconstruction ANDs')
