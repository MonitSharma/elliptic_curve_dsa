import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;models=r.parent/'breakthrough-live-core-rank-20261020';native=r.parent/'breakthrough-fin1-loan-native-20261020';f={k:int(v,16)for k,v in json.loads((models/'FUNCTIONS.json').read_bytes()).items()};m=json.loads((native/'MODEL-CERTIFICATE.json').read_bytes());values=[f['one']]+[f[f'input{i}']for i in range(14)]+[f[n]for n in m['new_helper_names']];basis={}
for i,v in enumerate(values):
 mask=1<<i
 while v:
  h=v.bit_length()-1
  if h not in basis:basis[h]=(v,mask);break
  w,b=basis[h];v^=w;mask^=b
rows=[]
for i in range(21):
 v=f[f'field{i}'];mask=0
 while v:w,b=basis[v.bit_length()-1];v^=w;mask^=b
 assert mask>>35==0;rows.append(mask)
raw=(native/'certificate.rs').read_bytes()+('const F1_FIELDS:&[u64]=&['+','.join(hex(v)for v in rows)+'];\n').encode();(r/'certificate.rs').write_bytes(raw);(r/'MODEL-CERTIFICATE.json').write_text(json.dumps({'status':'EXACT_FIELD_COORDINATES_MODEL','native_certificate_sha256':hashlib.sha256((native/'certificate.rs').read_bytes()).hexdigest(),'source_functions_sha256':hashlib.sha256((models/'FUNCTIONS.json').read_bytes()).hexdigest(),'certificate_sha256':hashlib.sha256(raw).hexdigest(),'retained_c6_index':m['new_helper_names'].index('c6'),'scope':'Twenty retained forms provide all21 addend fields plusC6. Native complete-fold tests pending.'},indent=2)+'\n');assert m['new_helper_names'].index('c6')==19
