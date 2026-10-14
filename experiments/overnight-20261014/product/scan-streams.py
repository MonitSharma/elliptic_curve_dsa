"""Read zstd framed official streams; report emitted and depth-weighted diagnostics.

No simulator, score, test packets or nonce selection is performed. Uses libzstd
through ctypes to avoid requiring a new package in the server environment.
"""
import argparse,ctypes as c,ctypes.util,hashlib,json,struct
from collections import Counter
from pathlib import Path

class Buffer(c.Structure):
    _fields_=[('src',c.c_void_p),('size',c.c_size_t),('pos',c.c_size_t)]

def records(path):
    z=c.CDLL(ctypes.util.find_library('zstd'))
    z.ZSTD_createDStream.restype=c.c_void_p
    z.ZSTD_initDStream.argtypes=[c.c_void_p];z.ZSTD_initDStream.restype=c.c_size_t
    z.ZSTD_decompressStream.argtypes=[c.c_void_p,c.POINTER(Buffer),c.POINTER(Buffer)]
    z.ZSTD_decompressStream.restype=c.c_size_t
    z.ZSTD_isError.argtypes=[c.c_size_t];z.ZSTD_isError.restype=c.c_uint
    z.ZSTD_freeDStream.argtypes=[c.c_void_p]
    stream=z.ZSTD_createDStream();assert stream
    try:
        assert not z.ZSTD_isError(z.ZSTD_initDStream(stream))
        with open(path,'rb') as f:
            header=f.read(16);assert header[:8]==b'QECCOPSZ'
            expected=struct.unpack('<Q',header[8:])[0];seen=0;pending=b''
            outmem=c.create_string_buffer(56*16384)
            while chunk:=f.read(1024*1024):
                inmem=c.create_string_buffer(chunk);inp=Buffer(c.cast(inmem,c.c_void_p),len(chunk),0)
                while inp.pos<inp.size:
                    out=Buffer(c.cast(outmem,c.c_void_p),len(outmem),0)
                    status=z.ZSTD_decompressStream(stream,c.byref(out),c.byref(inp))
                    assert not z.ZSTD_isError(status)
                    data=pending+outmem.raw[:out.pos];complete=len(data)//56*56
                    for op in struct.iter_unpack('<II6Q',data[:complete]):
                        seen+=1;yield op
                    pending=data[complete:]
            assert not pending and seen==expected,(seen,expected,len(pending))
    finally:z.ZSTD_freeDStream(stream)

def counts(path):
    kinds=Counter();depth=0;expected=0.;maxq=-1;maxbit=-1
    for op in records(path):
        k,_,q2,q1,t,ct,cond,rt=op;kinds[k]+=1
        for q in (q2,q1,t):
            if q!=2**64-1:maxq=max(maxq,q)
        for b in (ct,cond):
            if b!=2**64-1:maxbit=max(maxbit,b)
        if k==15:depth+=1
        elif k==16:depth-=1
        elif k in (13,14):expected+=2.**(-depth-int(cond!=2**64-1))
        assert depth>=0
    assert depth==0
    return dict(operations=sum(kinds.values()),kind_counts=dict(kinds),emitted_toffolis=kinds[13]+kinds[14],condition_depth_proxy=expected,qubits_touched=maxq+1,bits_touched=maxbit+1,stream_sha256=hashlib.file_digest(open(path,'rb'),'sha256').hexdigest(),scope='Diagnostic emitted/depth-weighted count; not a scored mean or width benchmark.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stream');p.add_argument('--out',required=True);a=p.parse_args()
    result=counts(a.stream);Path(a.out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
