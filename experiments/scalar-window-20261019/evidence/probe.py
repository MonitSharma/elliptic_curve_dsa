"""One process per immutable table; fresh synthetic inputs, no nonce packet."""
import ctypes as c,hashlib,json,resource,sys,time
from pathlib import Path
r=Path(__file__).resolve().parent;kind=sys.argv[1];width=int(sys.argv[2]);assert (kind,width) in [('frozen',20),('extended',20),('extended',22),('extended',24)]
path=r.parent/'scalar-fast-20261015/libscalar_fast_batch.so' if kind=='frozen' else r/'libscalar_extended.so'
lib=c.CDLL(str(path));init=lib.scalar_fast_fixed_init;init.argtypes=[c.c_uint];init.restype=c.c_int
pairs=lib.scalar_fast_pairs;pairs.argtypes=[c.c_uint,c.c_void_p,c.c_void_p];pairs.restype=c.c_int
start=time.perf_counter();assert init(width)==1;startup=time.perf_counter()-start
times=[];fingerprints=[];sizes=[]
for trial in range(5):
    # Five distinct corpora avoid timing one small cache-hot repeated lookup set.
    count=131072;raw=bytearray(hashlib.shake_256(b'scalar-window-public-fresh-20261019-v1'+trial.to_bytes(8,'little')).digest(count*64))
    for i,v in enumerate([0,1,2,3,(1<<256)-1]+[1<<j for j in range(256)]+[((1<<256)-1)^(1<<j) for j in range(256)]):
        raw[64*i:64*i+32]=v.to_bytes(32,'big')
        raw[64*i+32:64*i+64]=((v*17+5)%((1<<256)-1)).to_bytes(32,'big')
    input_array=(c.c_uint8*len(raw)).from_buffer(raw);out=(c.c_uint8*(count*192))()
    begin=time.perf_counter()
    for at in range(0,count,64):assert pairs(64,c.byref(input_array,at*64),c.byref(out,at*192))==1
    times.append(time.perf_counter()-begin);data=bytes(out);fingerprints.append(hashlib.sha256(data).hexdigest())
    target=r/f'reference-{trial}.bin'
    if kind=='frozen':assert not target.exists();target.write_bytes(data)
    else:assert target.read_bytes()==data,(kind,width,trial)
    for n in [1,3,7,8,9,63]:
        partial=(c.c_uint8*(n*192))();assert pairs(n,input_array,partial)==1;assert bytes(partial)==data[:n*192]
    sizes.append(count)
result={'status':'EXACT_PUBLIC_POINTS_MATCH_FROZEN_REFERENCE' if kind!='frozen' else 'FROZEN_REFERENCE_CREATED','kind':kind,'window':width,'startup_seconds':startup,
 'times_seconds':times,'shots_each_trial':sizes,'fresh_corpora':5,'total_pairs':sum(sizes),'output_sha256':fingerprints,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
 'partial_batches_match':True,'library_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Synthetic public-input table benchmark; no circuit, nonce packet, score or active runtime change.'}
(r/f'{kind}-{width}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
