from pathlib import Path
import json,struct,ctypes,ctypes.util,hashlib
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016');NONE=2**64-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();h=hashlib.sha256(d).hexdigest();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw,h
old,oldhash=load(r.parent/'product-exact-20261015/tip/ops.bin');new,newhash=load(r/'candidate/ops.bin')
assert oldhash=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e';assert newhash=='12840968ed58bb2063128d133a8f493bce3ed90256ee3b03bb5dcdc3f40dc30e'
sites=sorted(json.loads((r/'flag-regions.json').read_text()),key=lambda s:s['final_start']);profile=json.loads((r/'family-cost-profile.json').read_text());guards={s['final_at']:s['guard']for s in profile['actual_sites']}
expected=[]
for j,s in enumerate(sites):
 g=guards[s['final_start']+2];assert g['kind']=='exact'and g['scope_depth']==1 and len(g['predicate'])==1;tag,first,positive=g['predicate'][0];assert tag=='M'and positive
 old_count=2*s['k']-1;expected.append(dict(site=s['site'],old_MR_cut=first+old_count,new_MR_ordinal=first+old_count+j,new_op=s['final_start']+16*j+s['old_ops']+7,old_start=s['final_start'],old_end=s['final_end']))
allowed_refs={e['new_op']for e in expected}|{e['new_op']+1 for e in expected};oldABI=[];newABI=[];oldbounds=[0,0];newbounds=[0,0]
def old_mr():
 for at,o in enumerate(struct.iter_unpack('<7Q',old)):
  for q in o[1:4]:
   if q!=NONE:oldbounds[0]=max(oldbounds[0],q+1)
  for b in o[4:6]:
   if b!=NONE:oldbounds[1]=max(oldbounds[1],b+1);assert b<45701
  if o[0]in(1,2):oldABI.append(o)
  if o[0]in(11,12):yield at,o
oldit=old_mr();original=0;physical=0;extras=[]
for at,o in enumerate(struct.iter_unpack('<7Q',new)):
 for q in o[1:4]:
  if q!=NONE:newbounds[0]=max(newbounds[0],q+1)
 for b in o[4:6]:
  if b!=NONE:newbounds[1]=max(newbounds[1],b+1)
 if o[4]==45701 or o[5]==45701:assert at in allowed_refs
 if o[0]in(1,2):newABI.append(o)
 if o[0]not in(11,12):continue
 if o[0]==12 and o[4]==45701:
  e=expected[len(extras)];assert(at,physical,original)==(e['new_op'],e['new_MR_ordinal'],e['old_MR_cut']);extras.append(dict(**e,new_HMR=list(o)))
 else:
  old_at,old_op=next(oldit);assert o==old_op,('original physical MR operation changed',old_at,at,original);original+=1
 physical+=1
assert next(oldit,None)is None;assert original==906156 and physical==906168 and len(extras)==12;assert oldbounds==[1234,45701]and newbounds==[1234,45702];assert oldABI==newABI
out=dict(proved=True,old_stream_sha256=oldhash,new_stream_sha256=newhash,old_ops=len(old)//56,new_ops=len(new)//56,old_quantum_and_classical_bounds=oldbounds,new_quantum_and_classical_bounds=newbounds,ABI_register_operations_byte_identical=True,all_original_R_HMR_operations_byte_identical_in_order=True,all_original_MR_consumed_even_if_inactive=True,new_bit_absent_from_old_namespace=True,new_bit_referenced_only_by12_added_HMR_and12_added_Push=True,old_physical_MR=original,new_physical_MR=physical,extra_MR=extras,projection='Delete these12 physical MR ordinals; every retained R/HMR instruction is byte-identical to the next original instruction. Classical/scope equivalence follows the separately bound universal local transducer proof.')
(r/'global-MR-map-proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='extra_MR'},indent=2))
