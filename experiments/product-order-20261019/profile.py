"""Read-only structural profile to explain scheduler cost; no packet inputs."""
import ctypes,ctypes.util,hashlib,json,os,struct,time
from pathlib import Path
import numpy as np
r=Path(__file__).resolve().parent;p=r.parent/'product-pareto-20261019/parent/ops.bin'
assert int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))>160*1024**2
start=time.time();data=p.read_bytes();assert hashlib.sha256(data).hexdigest()=='99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0]
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,n*56,data[16:],len(data)-16)==n*56
rows=np.frombuffer(out,dtype='<u8').reshape(n,7);kind=rows[:,0];no=2**64-1
def width(columns):
    return int(max((np.max(col[col!=no]) if np.any(col!=no) else -1) for col in columns))+1
bar=np.flatnonzero(np.isin(kind,[0,1,2,15,16,17]));lengths=np.diff(np.concatenate(([-1],bar,[n])))-1
result={'status':'SOURCE_STRUCTURE_PROFILE_ONLY','ops':n,'num_qubits':width([rows[:,1],rows[:,2],rows[:,3]]),
    'num_bits':width([rows[:,4],rows[:,5]]),'counts_by_kind':np.bincount(kind.astype(np.int64),minlength=18).tolist(),
    'barriers':len(bar),'segments':len(lengths),'nonempty_segments':int(np.count_nonzero(lengths)),
    'max_segment':int(lengths.max()),'segment_length_quantiles':np.quantile(lengths,[.5,.9,.99,1]).tolist(),
    'elapsed_seconds':time.time()-start,'scheduler_note':'Initial implementation allocates slot-sized dependency arrays per nonempty segment; short segments can dominate runtime.'}
(r/'STRUCTURE-PROFILE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
