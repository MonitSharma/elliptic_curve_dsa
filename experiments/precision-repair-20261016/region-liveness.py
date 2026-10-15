from pathlib import Path
import ctypes,ctypes.util,struct,json
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
rows=json.loads((root/'surviving-folds.json').read_text())['rows'];sites=[r for r in rows if r.get('admitted_for_further_study')];body=load(root.parent/'product-exact-20261015/tip/ops.bin');none=(1<<64)-1
writes={};reads={};qreads={};qset={}
for i in range(len(body)//56):
 k,a,b,t,ct,cc,rt=struct.unpack_from('<7Q',body,i*56)
 if ct!=none:writes.setdefault(ct,[]).append(i)
 if cc!=none:reads.setdefault(cc,[]).append(i)
 for q in (a,b,t):
  if q!=none:qset.setdefault(q,[]).append(i)
for r in sites:
 a=r['final_start'];b=a+r['ops'];inside={ct for ct,v in writes.items()if any(a<=x<b for x in v)}
 external=[dict(bit=ct,reads_before=[x for x in reads.get(ct,[])if x<a],reads_after=[x for x in reads.get(ct,[])if x>=b],writes_outside=[x for x in writes[ct]if x<a or x>=b])for ct in inside if any(x<a or x>=b for x in reads.get(ct,[]))or any(x<a or x>=b for x in writes[ct])]
 r['written_bits']=sorted(inside);r['external_classical_liveness']=external;r['all_written_bits_local']=not external
result=dict(sites=len(sites),local_written_bits=sum(r['all_written_bits_local']for r in sites),rows=sites,quantum_borrowed_lifetime_proof=False)
(root/'region-liveness.json').write_text(json.dumps(result,indent=2)+'\n');print('REGION_LIVENESS',result['sites'],result['local_written_bits']);print('TOP1',json.dumps([r for r in sites if not r['reverse']and r['tick']==1]))
