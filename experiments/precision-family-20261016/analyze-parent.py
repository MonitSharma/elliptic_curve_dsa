from pathlib import Path
import ctypes,ctypes.util,struct,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-family-20261016');old=root.parent/'precision-repair-20261016';none=(1<<64)-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(old/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');m=json.loads((old/'surviving-folds.json').read_text());allrows=[r for r in m['rows']if not r['reverse']and r['tick']>=100];rows=[r for r in allrows if r['found']and r['empty_balanced_boundaries']]
queries=[r['final_start']for r in rows];nq=1234;nb=1+max(v for k,a,b,t,bt,bc,rt in struct.iter_unpack('<7Q',final)for v in[bt,bc]if v!=none)
lib=ctypes.CDLL(str(root/'constant_zero.so'));lib.constant_zeros.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t),ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p];lib.constant_zeros.restype=ctypes.c_int
initialq=(ctypes.c_int8*nq)();initialb=(ctypes.c_int8*nb)();regs={}
for k,a,b,t,bt,bc,rt in struct.iter_unpack('<7Q',final):
 if k==2:
  assert rt!=none
  if t!=none:initialq[t]=-1;regs.setdefault(rt,[]).append(['Qubit',t])
  if bt!=none:initialb[bt]=-1;regs.setdefault(rt,[]).append(['Bit',bt])
assert sorted(regs)==[0,1,2,3]and all(len(v)==256 for v in regs.values())
q=(ctypes.c_size_t*len(queries))(*queries);result=ctypes.create_string_buffer(len(queries)*nq);assert lib.constant_zeros(final,len(final)//56,nq,nb,q,len(queries),result,initialq,initialb)==0
records=[]
for i,r in enumerate(rows):
 block=raw[r['start']*56:r['end']*56];used={v for row in struct.iter_unpack('<7Q',block)for v in row[1:4]if v!=none};zeros=[j for j in range(nq)if result.raw[i*nq+j]and j not in used]
 records.append(dict(tick=r['tick'],raw_begin=r['start'],raw_end=r['end'],final_begin=r['final_start'],final_end=r['final_start']+r['ops'],raw_sha256=r['raw_sha256'],donor_candidates=zeros,zero_proof='conservative whole-final-stream constant propagation; ALL declared input registers arbitrary, protected Simulator initial auxiliaryq/b zero; everyMR outcome arbitrary; no input corpus',q_touched=sorted(used)))
family=dict(source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',family='A: one extra bit at all complete unchanged late-forward fold regions with certified donor/interfaces',structural_predicate='!reverse && tick>=100 && unique full old-region byte identity && empty balanced original/final scope boundaries',eligible_structural_ticks=[r['tick']for r in records],excluded_inherited_overlap=[r['tick']for r in allrows if not r['found']],frozen_before_donor_generation=True,donor_policy='existing active, unused original region, provedzero for arbitrary input/MR, not nextpayloadbit, restoredzero at exit',on_failure='preserve rejection; never silently omit an admitted site',initial_registers=regs,records=records)
(root/'FAMILY-A.json').write_text(json.dumps(family,indent=2)+'\n');(root/'donor-candidates.txt').write_text(''.join(str(r['tick'])+' '+','.join(map(str,r['donor_candidates']))+'\n'for r in records));print('FAMILY_A',len(records),'EXCLUDED',family['excluded_inherited_overlap'],'ZERO_CANDIDATES',[(r['tick'],len(r['donor_candidates']))for r in records])
