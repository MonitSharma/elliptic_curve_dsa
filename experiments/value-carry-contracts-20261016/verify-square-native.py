from pathlib import Path
import json,struct,hashlib,subprocess
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016')
assert(r/'square-native.exit').read_text().strip()=='0'
assert(r/'square-guard-tests.exit').read_text().strip()=='0'
exec((r/'analyze-square.py').read_text().split('rawpath=')[0])
parent=load(r.parent/'product-exact-20261015/tip/ops.bin');native=load(r/'square4-candidate/ops.bin');info=json.loads((r/'square-interfaces.json').read_text());receipt=json.loads((r/'square-predicted-receipt.json').read_text())
assert hashlib.sha256(native).hexdigest()==receipt['expected_candidate_canonical_sha256']
assert len(native)==len(parent)+16*56
cursor=offset=0;records=[]
for row in sorted(info['rows'],key=lambda x:x['actual_terminal']):
 at=row['actual_terminal'];p=row['previous'];a=row['penultimate'];t=row['top_bit'];u=row['next']
 def ccx(x,y,z):return struct.pack('<7Q',13,x,y,z,N,N,N)
 expected=(ccx(p,a,0)+ccx(0,t,u))*2+ccx(p,a,t)
 assert native[cursor*56:(at+offset)*56]==parent[(cursor-offset)*56:at*56]
 assert native[(at+offset)*56:(at+offset+5)*56]==expected
 assert parent[at*56:(at+1)*56]==ccx(p,a,t)
 records.append(dict(old_original_at=at,new_original_at=at+offset+4,new_inserted_at=at+offset,extra_ops=4,all_old_MR_ordinals_unchanged=True))
 cursor=at+offset+5;offset+=4
assert native[cursor*56:]==parent[(cursor-offset)*56:]
mr=lambda d:[o for o in struct.iter_unpack('<7Q',d)if o[0]in[11,12]]
pm,nm=mr(parent),mr(native);assert pm==nm and len(pm)==906156
def stats(data):
 nq=nb=tof=0;abi=[]
 for o in struct.iter_unpack('<7Q',data):
  k,a,b,t,bt,bc,rt=o
  if k in[13,14]:tof+=1
  for q in[a,b,t]:
   if q!=N:nq=max(nq,q+1)
  for bit in[bt,bc]:
   if bit!=N:nb=max(nb,bit+1)
  if k in[1,2]:abi.append(o)
 return nq,nb,tof,abi
pa,na=stats(parent),stats(native);assert na[:2]==pa[:2]==(1234,45701);assert na[2]==pa[2]+16;assert na[3]==pa[3]
source=json.loads((r/'square4-source.json').read_text())
for name,sha in source['files'].items():assert hashlib.sha256((r/'square4-candidate'/name).read_bytes()).hexdigest()==sha
modified=subprocess.check_output(['git','-C',str(r/'square4-candidate'),'diff','--name-only'],text=True).splitlines();assert modified and all(x.startswith('src/point_add/')for x in modified)
f=json.loads((r/'SQUARE4-PREDECLARATION.json').read_text())
for name,sha in f['proof_files'].items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==sha
out=dict(status='NATIVE COMPLETE CIRCUIT PASS; NO CENSUS OR RECORD CLAIM',sha256=hashlib.sha256((r/'square4-candidate/ops.bin').read_bytes()).hexdigest(),canonical_sha256=hashlib.sha256(native).hexdigest(),ops=len(native)//56,Q=1234,B=45701,
 original_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',
 added_generated_CCX=16,added_expected_T=16,added_Q=0,added_MR=0,all_original906156_MR_instructions_and_ordinals_identical=True,
 removing_only16_inserted_CCX_recovers_every_original_op=True,all_original_classical_scope_ABI_ops_byte_identical=True,identity_tail_byte_identical=True,source_hashes_rechecked=True,only_point_add_changed=True,
 full_pre_tail_input_shake256_32=receipt['input_pre_tail_shake256_32'],family_predeclaration_sha256=receipt['family_predeclaration_sha256'],records=records,
 arithmetic='exact one-bit wider truncated signed addition per C130 window when incoming source carries have their defined arithmetic meaning; local frame/dirty-donor/value/phase theorem is unconditional',
 higher_payload_bits='all bits above each new nextU are unchanged by that local replacement; later original windows still run and may intentionally read earlier corrected outputs',
 old_arithmetic_mask_transferred=False)
(r/'square-native-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
