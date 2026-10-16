from pathlib import Path
import json,hashlib,ctypes,struct,time,statistics
r=Path(__file__).resolve().parents[1];d=r/'a29-conditional-coverage-v1';up=r.parent/'product-exact-20261015/repair53-native-20261016'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original_meta=json.loads((r/'packets/all-failing-tip.metadata.json').read_text());original_rows=(r/'packets/all-failing-tip.tsv').read_text().splitlines();assert len(original_meta)==len(original_rows)==541
points=[]
for row,meta in zip(original_rows,original_meta):
 if meta['value']:
  coords=[int(x,16)for x in row.split()[1:]];assert len(coords)==6;points.append(dict(group='old431',batch=meta['batch'],lane=meta['lane'],coords=coords))
assert len(points)==431
comparison=json.loads((up/'PER_SHOT_FAILURE_COMPARISON.json').read_text());assert sha(up/'parent-census.jsonl')==comparison['parent_rows_sha256'];assert sha(up/'candidate-census.jsonl')==comparison['candidate_rows_sha256']
def failures(path):
 result={}
 for line in path.read_text().splitlines():
  row=json.loads(line)
  for f in row['failures']:
   if f['value']:result[(row['batch'],f['lane'])]=f
 return result
parent=failures(up/'parent-census.jsonl');candidate=failures(up/'candidate-census.jsonl');only=sorted(parent.keys()-candidate.keys());assert len(parent)==3553 and len(candidate)==3539 and len(only)==14 and not(candidate.keys()-parent.keys())
scalarpath=r.parent/'scalar-fast-20261015/libscalar_fast_batch.so';assert sha(scalarpath)=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f';scalar=ctypes.CDLL(str(scalarpath));scalar.scalar_fast_fixed_init.argtypes=[ctypes.c_uint];scalar.scalar_fast_fixed_init.restype=ctypes.c_int;assert scalar.scalar_fast_fixed_init(16)==1;scalar.scalar_fast_pairs.argtypes=[ctypes.c_uint,ctypes.c_void_p,ctypes.c_void_p];scalar.scalar_fast_pairs.restype=ctypes.c_int
pairs=b''.join(int(parent[key][name],16).to_bytes(32,'big')for key in only for name in['k1','k2']);inp=ctypes.create_string_buffer(pairs);out=ctypes.create_string_buffer(14*192);assert scalar.scalar_fast_pairs(14,inp,out)==1
for j,key in enumerate(only):
 coords=[int.from_bytes(out.raw[j*192+i*32:j*192+(i+1)*32],'big')for i in range(6)];points.append(dict(group='repair14',batch=key[0],lane=key[1],k1=parent[key]['k1'],k2=parent[key]['k2'],coords=coords))
assert len(points)==445
(d/'fixed445-inputs.tsv').write_text(''.join(str(i)+' '+' '.join(f'{x:064x}'for x in p['coords'])+'\n'for i,p in enumerate(points)))
guardpath=r/'a29-conditional-prefix-v1/public-discrepancy-guard.bin';assert sha(guardpath)=='355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3';data=guardpath.read_bytes();assert data[:8]==b'MRMASK01';n,np,nr=struct.unpack_from('<QQQ',data,8);assert(np,nr)==(1024,1);root=struct.unpack_from('<I',data,32+n*16)[0];assert len(data)==32+n*16+4
libpath=r.parent/'mask-evaluator-20261016/libmask8.so';assert sha(libpath)=='641f8c1b6578c9878244650bd05cbbbd1fd452e9199c504bc76832cf72fd81e1';lib=ctypes.CDLL(str(libpath));U=ctypes.c_uint64;lib.mask8_eval.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(U),ctypes.c_size_t,ctypes.POINTER(U),ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,ctypes.POINTER(U)];lib.mask8_eval.restype=ctypes.c_int
nodes=ctypes.create_string_buffer(data[32:32+n*16]);ports=(U*(1024*8))();values=(U*(n*8))();roots=(ctypes.c_uint32*512)(*[root]*512);output=(U*(512*8))()
for lane,p in enumerate(points):
 for coord,x in enumerate(p['coords'][:4]):
  for bit in range(256):
   if x>>bit&1:ports[(coord*256+bit)*8+lane//64]|=1<<(lane%64)
def run():
 start=time.perf_counter();code=lib.mask8_eval(nodes,n,ports,1024,values,n,roots,512,output);elapsed=time.perf_counter()-start;assert code==0;assert all(output[i*8+j]==output[j]for i in range(512)for j in range(8));return elapsed
cold=run();times=[run()for _ in range(9)];guard_words=list(output[:8])
for lane,p in enumerate(points):p['discrepancy_guard']=bool(guard_words[lane//64]>>(lane%64)&1)
# Independent scalar binary interpretation on an existing packed64-input group.
group=next((i for i,w in enumerate(guard_words)if w),0);v=[]
for i in range(n):
 k,a,b,aux=struct.unpack_from('<4I',data,32+i*16);assert aux==0
 if k==0:x=0
 elif k==1:x=(1<<64)-1
 elif k==2:assert a<1024;x=ports[a*8+group]
 else:
  assert k in[3,4,5]and a<i and b<i;x=v[a]^v[b]if k==3 else v[a]&v[b]if k==4 else v[a]|v[b]
 v.append(x)
assert v[root]==guard_words[group]
old=[p for p in points if p['group']=='old431'];rep=[p for p in points if p['group']=='repair14'];old_true=sum(p['discrepancy_guard']for p in old);rep_true=sum(p['discrepancy_guard']for p in rep)
result=dict(status='EXISTING_FIXED_WITNESSES_DESCRIPTIVE_GUARD_COVERAGE_AND_COMPONENT_COST_ONLY',guard_sha256=sha(guardpath),guard_nodes=n,label_14=comparison['label'],parent_rows_sha256=comparison['parent_rows_sha256'],candidate_rows_sha256=comparison['candidate_rows_sha256'],old_value_witnesses=dict(total=431,guard_false=431-old_true,guard_true=old_true,previously_certified_by_old_mask=421,conservative_retained_old_certificates_lower_bound=max(0,421-old_true)),parent_only_value_lanes=dict(total=14,guard_false=14-rep_true,guard_true=rep_true),guard_only_timings=dict(cold_seconds=cold,repeated_9_seconds=times,median_seconds=statistics.median(times),median_us_per_real_point=statistics.median(times)*1e6/445,points_per_vector=445,capacity=512,conditions='SingleCcore, same445distinctfixedinputs repeated9times, allocation and inputpacking excluded; no end-to-end or fresh-input throughput claim.'),independent_scalar_binary_group=group,independent_scalar_binary_matches_C=True,root_repeat_wrapper='Immutable kernel requires512roots; repeated the same soleGroot512times in temporarymemory, unchangedguardartifact.',polarity='G=1 excludes transfer; G=0 permits the new source-chain theorem once independently accepted.',descriptive_limits='G=1 only excludes this sufficient equality certificate; it does not prove a final intrinsic arithmetic difference or causal repair. G=0 with a physical-MR value-fix is consistent with measurement-tape coupling. No new census, eligibility sample, source or submission.',points=points)
(d/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='points'}))
