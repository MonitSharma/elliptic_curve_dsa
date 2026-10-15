"""Temporal classical liveness; physical measurement IDs are heavily reused."""
from pathlib import Path
import ctypes,ctypes.util,struct,json,bisect,time
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
d=(root.parent/'product-exact-20261015/tip/ops.bin').read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;body=o.raw;del o,d
rows=json.loads((root/'surviving-folds.json').read_text())['rows'];sites=[r for r in rows if r.get('admitted_for_further_study')];none=(1<<64)-1
writes={};reads={};kills={};depth=0
for i in range(n):
 k,a,b,t,ct,cc,rt=struct.unpack_from('<7Q',body,i*56)
 if ct!=none:
  writes.setdefault(ct,[]).append(i)
  if k==3:reads.setdefault(ct,[]).append(i)
  if k in (4,5,12)and cc==none and depth==0:kills.setdefault(ct,[]).append(i)
 if cc!=none:reads.setdefault(cc,[]).append(i)
 if k==15:depth+=1
 if k==16:depth-=1;assert depth>=0
assert depth==0
def next_at(v,at):
 i=bisect.bisect_left(v,at);return v[i]if i<len(v)else n+1
for r in sites:
 a=r['final_start'];b=a+r['ops'];inside={ct for ct,v in writes.items()if next_at(v,a)<b};details=[]
 for ct in sorted(inside):
  first_kill=next_at(kills.get(ct,[]),a);first_read=next_at(reads.get(ct,[]),a)
  next_kill=next_at(kills.get(ct,[]),b);next_read=next_at(reads.get(ct,[]),b)
  details.append(dict(bit=ct,live_in=first_read<min(first_kill,b),live_out=next_read<next_kill,first_read=first_read,first_unconditional_kill=first_kill,next_read=next_read,next_unconditional_kill=next_kill))
 r['classical_versions']=details;r['all_written_versions_local']=all(not d['live_in']and not d['live_out']for d in details)
result=dict(sites=len(sites),local_written_versions=sum(r['all_written_versions_local']for r in sites),rows=sites,quantum_borrowed_lifetime_proof=False,unconditional_kill_required=True)
(root/'version-liveness.json').write_text(json.dumps(result,indent=2)+'\n');print('VERSION_LIVENESS',result['sites'],result['local_written_versions']);print('TOP1',json.dumps([{k:v for k,v in r.items()if k in ['reverse','tick','classical_versions','all_written_versions_local']}for r in sites if not r['reverse']and r['tick']==1]))
