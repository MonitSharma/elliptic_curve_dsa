import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-live-core-rank-20261020';f={k:int(v,16)for k,v in json.loads((old/'FUNCTIONS.json').read_bytes()).items()};m=json.loads((r.parent/'breakthrough-core-loan-native-20261020/MODEL-CERTIFICATE-SPARSE.json').read_bytes());one=f['one'];low=[f['input0']^f['input6'],f['input1']^f['input7']^f['c1'],f['input2']^f['input8']^f['c2'],f['input3']^f['c3'],f['input4']^f['c4']^f['k0'],f['input5']^f['c5']^f['k0']^f['k1']];features=[one]+[f[f'input{i}']for i in range(6,14)]+low+[f[n]for n in m['new_helper_basis_names']];basis={}
for i,v in enumerate(features):
 mask=1<<i
 while v:
  h=v.bit_length()-1
  if h not in basis:basis[h]=(v,mask);break
  w,b=basis[h];v^=w;mask^=b
def coords(v):
 mask=0
 while v:
  w,b=basis[v.bit_length()-1];v^=w;mask^=b
 assert mask>>35==0
 return mask
rows=[coords(f[f'field{i}'])for i in range(21)];out=(r.parent/'breakthrough-core-loan-native-20261020/certificate-sparse.rs').read_bytes();out+=('const CORE_LOAN_FIELDS:&[u64]=&['+','.join(hex(v)for v in rows)+'];\n').encode();(r/'certificate.rs').write_bytes(out)
(r/'MODEL-CERTIFICATE.json').write_text(json.dumps({'status':'SOURCE_BOUND_VERIFIED_FIELD_COORDINATES','source_functions_sha256':hashlib.sha256((old/'FUNCTIONS.json').read_bytes()).hexdigest(),'certificate_sha256':hashlib.sha256(out).hexdigest(),'kept_physical_helpers':20,'erased_and_regenerated_helpers':11,'regeneration_ANDs':11,'scope':'21 source fields expressed using only retained20 forms and written low sums; no full-fold result yet.'},indent=2)+'\n')
