"""Source-function certificates for a thirty-helper fin1 prefix."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-live-core-rank-20261020';f={k:int(v,16)for k,v in json.loads((old/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];m=json.loads((old/'FIN1-MODEL.json').read_bytes());oldnames=[n for n in list(f)[15:46]if n!='c2'];newnames=m['selected_output_basis']+m['garbage_basis'];assert len(oldnames)==len(newnames)==30
original=[one]+[f[f'input{i}']for i in range(14)]+[f[n]for n in oldnames];basis={}
for i,v in enumerate(original):
 mask=1<<i
 while v:
  h=v.bit_length()-1
  if h not in basis:basis[h]=(v,mask);break
  w,b=basis[h];v^=w;mask^=b
 assert v
def coords(v,basis):
 mask=0
 while v:
  h=v.bit_length()-1;assert h in basis;w,b=basis[h];v^=w;mask^=b
 return mask
rows=[coords(f[n],basis)for n in newnames];mat=[v>>15 for v in rows];ops=[]
def xor(a,b):mat[b]^=mat[a];ops.append((a,b))
for i in range(30):
 j=next(j for j in range(i,30)if mat[j]>>i&1)
 if i!=j:xor(i,j);xor(j,i);xor(i,j)
 for j in range(30):
  if j!=i and mat[j]>>i&1:xor(i,j)
assert mat==[1<<i for i in range(30)];sim=[f[n]for n in oldnames]
for a,b in reversed(ops):sim[b]^=sim[a]
offset=[x&((1<<15)-1)for x in rows]
for i,mask in enumerate(offset):
 for j,v in enumerate(original[:15]):
  if mask>>j&1:sim[i]^=v
assert sim==[f[n]for n in newnames]
index={'one':0,**{f'input{i}':1+i for i in range(14)},**{n:15+i for i,n in enumerate(newnames)}}
erase={v['function']:v['phase_terms']for v in m['clifford_erasure_witnesses']};erase['c1']=[['input0','input6']];erase_order=['y5','c5','y4','y3','r3','r2','tt','c4','c3','c1'];out=['const F1_CX:&[(usize,usize)]=&'+repr(list(reversed(ops)))+';','const F1_OFFSETS:&[u64]=&['+','.join(hex(x)for x in offset)+'];','const F1_C1:usize='+str(newnames.index('c1'))+';','const F1_C3:usize='+str(newnames.index('c3'))+';','const F1_ERASE:&[(usize,Option<&[(usize,usize)]>)]=&[']
for name in erase_order:
 terms=erase.get(name);text='None'if name=='c3'else 'Some(&['+','.join('('+str(index[t[0]])+','+str(index[t[1]]if len(t)==2 else 0)+')'for t in terms)+'])';out.append('('+str(newnames.index(name))+','+text+'),')
out.append('];');out.append('const F1_REBUILD:&[(usize,u64,&[(u64,u64)])]=&[')
functions=[one]+[f[f'input{i}']for i in range(14)]+[f[n]for n in m['selected_output_basis']];available=list(range(35));witnesses=[]
forms={'c1':(f['input0'],f['input6'],0),'c4':(f['input3'],f['c3'],0),'tt':(f['input12'],f['input13'],0),'r2':(f['input10']^f['r1'],f['input1']^f['r1'],f['r1']),'r3':(f['input11']^f['r2'],f['input2']^f['r2'],f['r2']),'y3':(f['input12']^f['input13']^f['tt'],f['input3']^f['c3'],0),'y4':(f['input13'],f['input4']^f['c4']^f['k0'],0),'c5':(f['input4']^f['c4'],f['k0']^f['c4'],f['c4']),'y5':(f['tt'],f['input5']^f['c5']^f['k0']^f['k1'],0)}
for name in m['garbage_basis']:
 if name=='c3':out.append('('+str(newnames.index(name))+',0,&[]),')
 else:
  basis={}
  for v,j in zip(functions,available):
   mask=1<<j
   while v:
    h=v.bit_length()-1
    if h not in basis:basis[h]=(v,mask);break
    w,b=basis[h];v^=w;mask^=b
  left,right,linear=forms[name];assert (left&right)^linear==f[name];a,b,l=coords(left,basis),coords(right,basis),coords(linear,basis);out.append(f'({newnames.index(name)},{hex(l)},&[({hex(a)},{hex(b)})]),');witnesses.append(name)
 functions.append(f[name]);available.append(index[name])
out.append('];');(r/'certificate.rs').write_bytes(('\n'.join(out)+'\n').encode());(r/'expected.dat').write_bytes((' '.join(str((f[n]>>(64*i))&((1<<64)-1))for n in oldnames for i in range(256))+'\n').encode())
(r/'compressed.dat').write_bytes((' '.join(str((f[n]>>(64*i))&((1<<64)-1))for n in newnames[:20]for i in range(256))+'\n').encode())
assert f['c2']==(f['input1']&f['input7'])^(f['input1']&f['c1'])^(f['input7']&f['c1'])
assert f['c3']==(f['input2']&f['input8'])^(f['input2']&f['c2'])^(f['input8']&f['c2'])
report={'status':'EXACT_ALL_16384_TRUTH_FUNCTION_MODELS','functions_sha256':hashlib.sha256((old/'FUNCTIONS.json').read_bytes()).hexdigest(),'old_helper_names':oldnames,'new_helper_names':newnames,'prefix_helpers':30,'retained_helpers':20,'garbage_helpers':10,'clifford_erased_helpers':9,'special_erasure':'c3 needs c2=MAJ(acc1,E1,c1) regenerated only under its HMR bit, then cleaned; one conditional AND, at most30 helpers live. c1 remains until c3 is repaired.','reconstruction':'Nine one-product affine witnesses plus c3 via temporary c2 and one majority;11 unconditional AND products. Temporary c2 cleaned before remaining helpers refill.','certificate_sha256':hashlib.sha256((r/'certificate.rs').read_bytes()).hexdigest(),'expected_sha256':hashlib.sha256((r/'expected.dat').read_bytes()).hexdigest(),'scope':'Model only. Native prefix30, phase, reconstruction and peak controls pending.'};(r/'MODEL-CERTIFICATE.json').write_text(json.dumps(report,indent=2)+'\n');print('prefix30 / kept20 /9Clifford erasures +c3 conditional1AND repair /11AND reconstruction')
