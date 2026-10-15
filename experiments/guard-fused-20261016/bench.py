from pathlib import Path
import ctypes as c,struct,json,time,statistics,hashlib
d=Path(__file__).resolve().parent;p=d.parent/'prefilter-20261015'
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
assert sha(p/'libmask_fused.so')=='dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0'
rawlib=d.parent/'mask-evaluator-20261016/libmask8.so'
assert sha(rawlib)=='641f8c1b6578c9878244650bd05cbbbd1fd452e9199c504bc76832cf72fd81e1'
class Op(c.Structure):_fields_=[('k',c.c_uint32),('a',c.c_uint32),('b',c.c_uint32),('d',c.c_uint32)]
U=c.c_uint64;I=c.c_uint32;S=c.c_size_t
raw=c.CDLL(str(rawlib));raw.mask8_eval.argtypes=[c.POINTER(Op),S,c.POINTER(U),S,c.POINTER(U),S,c.POINTER(I),S,c.POINTER(U)];raw.mask8_eval.restype=c.c_int
fast=c.CDLL(str(p/'libmask_fused.so'));fast.mask_fused_eval.argtypes=[c.POINTER(Op),S,S,c.POINTER(U),S,c.POINTER(U),S,c.POINTER(I),S,c.c_uint,c.POINTER(U)];fast.mask_fused_eval.restype=c.c_int
source=bytearray((d/'guard512.bin').read_bytes());plan=bytearray((d/'guard-fused.bin').read_bytes())
assert source[:8]==b'MRMASK01' and plan[:8]==b'MRSLOT02';assert plan[8:40]==hashlib.sha256(source).digest()
n,np,nr=struct.unpack_from('<QQQ',source,8);ni,ns,pp,rr=struct.unpack_from('<QQQQ',plan,40)
assert np==pp==1024 and nr==rr==512 and ns<65536
nodes=(Op*n).from_buffer(source,32);ops=(Op*ni).from_buffer(plan,72)
roots=(I*nr).from_buffer(source,32+n*16);slotroots=(I*nr).from_buffer(plan,72+ni*16)
values=(U*(n*8))();workspace=(U*(ns*8))();ref=(U*(nr*8))();out=(U*(nr*8))()
fixture=p/'a29-conditional-coverage-v1/fixed445-inputs.tsv';assert sha(fixture)=='f958e8665b8d9c7af59e848bddd4864e9fe951db3a835832933d6418cae4a922'
points=[]
for i,line in enumerate(fixture.read_text().splitlines()):
 f=line.split();assert int(f[0])==i and len(f)==7;points.append([int(x,16)for x in f[1:5]])
assert len(points)==445
auditpath=p/'a29-conditional-prefix-v1/audit-input-u64le.bin'
assert sha(auditpath)=='b5a1e5c690727cd4ca6351152284f49090cca73c7b4be6a6bc3ab69a6b46897f'
audit=struct.unpack('<1024Q',auditpath.read_bytes())
def pack(pts):
 ports=(U*(1024*8))()
 for i,point in enumerate(pts):
  for reg,x in enumerate(point):
   for bit in range(256):ports[(reg*256+bit)*8+i//64]|=((x>>bit)&1)<<(i%64)
 return ports
def rawrun(ports):
 t=time.perf_counter();assert raw.mask8_eval(nodes,n,ports,np,values,n,roots,nr,ref)==0;return time.perf_counter()-t
def fastrun(ports,width):
 t=time.perf_counter();assert fast.mask_fused_eval(ops,ni,ns,ports,np,workspace,len(workspace),slotroots,nr,width,out)==0;return time.perf_counter()-t
checked=0;cases=[]
def compare(ports,width,count,name):
 global checked
 a=rawrun(ports);expected=list(ref);b=fastrun(ports,width)
 for root in range(512):
  for word in range(8):
   assert out[root*8+word]==(expected[root*8+word]if word<width else 0)
   checked+=1
 assert all(expected[root*8+word]==expected[word]for root in range(512)for word in range(8))
 cases.append({'case':name,'inputs':count,'width':width,'raw_seconds':a,'fused_seconds':b})
 return [bool(out[i//64]>>(i%64)&1)for i in range(count)]
for count in [1,11,32,63,64,65,128,445]:
 compare(pack(points[:count]),(count+63)//64,count,'fixed445-prefix-'+str(count))
ports=(U*(1024*8))()
for i,w in enumerate(audit):ports[i*8]=w
assert not any(compare(ports,1,32,'original32audit'))
ports=pack(points);flags=compare(ports,8,445,'fixed445-full8')
assert sum(flags[:431])==3 and all(flags[431:]) and sum(flags)==17
# Explicit polarity control: output is G, never knownness. Reversing the test
# changes all445 classifications and would wrongly retain the17 excluded cases.
safe=[not v for v in flags];assert sum(safe)==428 and not any(safe[431:])
assert sum(a!=b for a,b in zip(flags,safe))==445
negative=0
for width,cap in [(0,len(workspace)),(9,len(workspace)),(8,ns*8-1)]:
 assert fast.mask_fused_eval(ops,ni,ns,ports,np,workspace,cap,slotroots,nr,width,out)!=0;negative+=1
old=ops[0].k;ops[0].k=99
assert fast.mask_fused_eval(ops,ni,ns,ports,np,workspace,len(workspace),slotroots,nr,8,out)!=0;negative+=1;ops[0].k=old
old=slotroots[0];slotroots[0]=ns
assert fast.mask_fused_eval(ops,ni,ns,ports,np,workspace,len(workspace),slotroots,nr,8,out)!=0;negative+=1;slotroots[0]=old
# Same fixed445 input vector, alternating order, allocation/packing excluded.
timings={'raw_full512':[],'fused_full512':[],'fused_width7':[]}
for trial in range(9):
 order=list(timings)if trial%2==0 else list(reversed(timings))
 for mode in order:
  elapsed=rawrun(ports)if mode=='raw_full512' else fastrun(ports,8 if mode=='fused_full512'else 7)
  timings[mode].append(elapsed)
report={'status':'COMPONENT_ONLY_FUSED_GUARD_EXACT_REFERENCE_PARTIAL_POLARITY_AND_NEGATIVE_CONTROLS_PASS',
 'original_G_sha256':'355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3',
 'wrapper_sha256':hashlib.sha256(source).hexdigest(),'plan_sha256':hashlib.sha256(plan).hexdigest(),
 'kernel_sha256':sha(p/'libmask_fused.so'),'instructions':ni,'peak_slots':ns,
 'full512_workspace_bytes_raw':n*64,'full512_workspace_bytes_fused':ns*64,
 'compared_root_words':checked,'cases':cases,'runtime_negative_controls':negative,
 'polarity_controls':{'raw_G1':17,'safe_notG':428,'all14repaired_excluded':True,'inverted_polarity_changes':445},
 'component_timings':{'conditions':'Single core, existing445 fixed points, nine alternating repetitions, allocations/packing excluded; no new inputs or end-to-end/8thread/search forecast.',
 'all_seconds':timings,'median_seconds':{k:statistics.median(v)for k,v in timings.items()}},
 'new_sampling':False,'runtime_operational_edits':False,'new_authority':False}
(d/'RESULT.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in report.items()if k!='cases'}))
