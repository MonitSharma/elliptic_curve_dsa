"""Full active forward core on all fourteen independent source bits.

This is a source-derived Boolean model, pending independent native controls.
No census samples, arithmetic cuts, candidate changes or resource records.
"""
import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;source=r.parent/'breakthrough-phase-plan-native-20261020/y15-tests-v3.rs';text=source.read_bytes().decode().replace('\r','')
ninputs=14;count=1<<ninputs;one=(1<<count)-1;variables=[sum(1<<j for j in range(count)if j>>i&1)for i in range(ninputs)];a=variables[:6];e=variables[6:9];nm=variables[9:12];k1,k2=variables[12:];held=[]
def store(name,value):held.append((name,value));return value
def AND(name,a,b):return store(name,a&b)
def MAJ(name,a,b,c):return store(name,(a&b)^(a&c)^(b&c))
c1=AND('c1',a[0],e[0]);c2=MAJ('c2',a[1],e[1],c1);c3=MAJ('c3',a[2],e[2],c2);c4=AND('c4',a[3],c3)
tt=AND('tt',k1,k2);g1=k1^k2^tt;r1=AND('r1',nm[0],a[0]);k=[nm[0]^a[0],nm[1]^a[1]^r1];r2=MAJ('r2',nm[1],a[1],r1);k.append(nm[2]^a[2]^r2);r3=MAJ('r3',nm[2],a[2],r2)
a4=k[0];a5=k[1]^k[0];y3=AND('y3',g1,a[3]^c3);y4=AND('y4',k2,a[4]^c4^a4);c5=MAJ('c5',a[4],a4,c4);y5=AND('y5',tt,a[5]^c5^a5);c6=MAJ('c6',a[5],a5,c5)
p=r3^c3;k.append(y3^p);t=AND('t0',p,y3^c3);k.append(y4^t);t=AND('t1',t,y4^c3);k.append(y5^t);t=AND('t2',t,y5^c3);k.append(t);k.append(AND('k7',t,c3))
gate_body=re.search(r'const Y16_FWD_GATES:.*?=\s*\[(.*?)\];',text,re.S)[1];gates=[tuple(int(x,16)for x in p)for p in re.findall(r'\((0x[0-9a-f]+),\s*(0x[0-9a-f]+)\)',gate_body)];assert len(gates)==14
out_masks=[int(x,16)for x in re.findall(r'0x[0-9a-f]+',re.search(r'const Y16_FWD_OUT:.*?=\s*\[(.*?)\];',text,re.S)[1])];assert len(out_masks)==21
vals=[one]+k
def expr(m):
 value=0
 for i,v in enumerate(vals):
  if m>>i&1:value^=v
 return value
for i,(x,y)in enumerate(gates):vals.append(AND(f'program{i}',expr(x),expr(y)))
outputs=[expr(m)for m in out_masks];assert len(held)==31
names=['one']+[f'input{i}'for i in range(ninputs)]+[name for name,_ in held];functions=[one]+variables+[v for _,v in held];piv={};deps=[]
for j,v in enumerate(functions):
 coef=1<<j
 while v:
  h=v.bit_length()-1
  if h in piv:v^=piv[h][0];coef^=piv[h][1]
  else:piv[h]=(v,coef);break
 if not v:deps.append({'last_function':names[j],'relation':[name for i,name in enumerate(names)if coef>>i&1]})
def rank(fs):
 basis={}
 for v in fs:
  while v:
   h=v.bit_length()-1
   if h in basis:v^=basis[h]
   else:basis[h]=v;break
 return len(basis)
codes=[sum((v>>i&1)<<j for j,v in enumerate(k))for i in range(count)];support=sorted(set(v if v<128 else v-256 for v in codes))
encoded={name:hex(v)for name,v in zip(names,functions)};encoded.update({f'k{i}':hex(v)for i,v in enumerate(k)});encoded.update({f'field{i}':hex(v)for i,v in enumerate(outputs)})
(r/'FUNCTIONS.json').write_text(json.dumps(encoded,separators=(',',':'))+'\n')
report={'status':'SOURCE_DERIVED_PENDING_NATIVE_CONTROL','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'inputs':'acc0..5,E0..2,Nm0..2,k1,k2; all independent','input_cases':count,'held_helper_functions':len(held),'full_input_plus_held_rank':len(piv),'maximum_possible_rank':len(functions),'linear_dependencies':deps,'input_plus_output_rank':rank([one]+variables+outputs),'input_plus_k_rank':rank([one]+variables+k),'actual_k_support':support,'functions_sha256':hashlib.sha256((r/'FUNCTIONS.json').read_bytes()).hexdigest(),'scope':'Actual active forward prefix at fin0, no source/tables/cuts changed. Pending native verification before implementation or resource claims.'}
(r/'MODEL-RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['actual_k_support']},indent=2))
