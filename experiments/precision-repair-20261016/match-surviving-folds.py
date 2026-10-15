"""Conservative byte-identical full-fold survival screen; no mutations."""
from pathlib import Path
import ctypes,ctypes.util,struct,json,time,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016')
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
z.ZSTD_isError.argtypes=[ctypes.c_size_t];z.ZSTD_isError.restype=ctypes.c_uint
def load(p):
    data=p.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0]
    out=ctypes.create_string_buffer(n*56);src=data[16:]
    size=z.ZSTD_decompress(out,len(out),src,len(src));assert not z.ZSTD_isError(size),(p,size);assert size==n*56
    return out.raw
started=time.time();raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin')
marks={}
for line in (root/'fold-marks.tsv').read_text().splitlines():
    f=line.split('\t');at,id,before,rev,t=map(int,f[:5]);entry=marks.setdefault(id,dict(id=id,reverse=bool(rev),tick=t,width=len(f[5].split(','))))
    entry['start'if before else'end']=at
rows=[];sites=set()
for row in marks.values():
    a,b=row['start'],row['end'];block=raw[56*a:56*b];at=final.find(block);row.update(ops=b-a,raw_sha256=hashlib.sha256(block).hexdigest(),found=at>=0)
    if at>=0:
        assert at%56==0
        again=final.find(block,at+56);row.update(final_start=at//56,unique=again<0)
        sites.update([('raw',a),('raw',b),('final',at//56),('final',at//56+b-a)])
    rows.append(row)
    if len(rows)%32==0:print('MATCH_PROGRESS',len(rows),round(time.time()-started,3),flush=True)
snapshots={}
for mode,body in [('raw',raw),('final',final)]:
    wanted={pos for m,pos in sites if m==mode};stack=[];writes={};outer_valid=True
    for i in range(len(body)//56+1):
        if i in wanted:snapshots[(mode,i)]=list(stack)
        if i==len(body)//56:break
        kind=struct.unpack_from('<I',body,56*i)[0]
        if kind in [3,4,5,11,12]:
            c=struct.unpack_from('<Q',body,56*i+32)[0]
            if c!=(1<<64)-1:writes[c]=(i,hashlib.sha256(body[56*i:56*(i+1)]).hexdigest())
        if kind==15:
            bit=struct.unpack_from('<Q',body,56*i+40)[0];stack.append((bit,writes.get(bit)))
        if kind==16:
            assert stack,(mode,i);stack.pop()
    assert not stack,mode
for row in rows:
    if not row['found']:continue
    a,b=row['start'],row['end'];c=row['final_start'];d=c+row['ops']
    ss=[snapshots[k]for k in [('raw',a),('raw',b),('final',c),('final',d)]]
    # Empty boundary stacks are an exact identical-scope certificate. Nonempty
    # scopes require semantic snapshot equality and remain rejected here.
    row['boundary_stacks']=ss;row['empty_balanced_boundaries']=all(not s for s in ss)
    row['admitted_for_further_study']=row['unique']and row['empty_balanced_boundaries']
result=dict(raw_ops=len(raw)//56,final_ops=len(final)//56,sites=len(rows),byte_identical=sum(r['found']for r in rows),unique_empty_scope=sum(r.get('admitted_for_further_study',False)for r in rows),seconds=time.time()-started,rows=rows,replacement_implemented=False,source_bound_region_match_only=True)
(root/'surviving-folds.json').write_text(json.dumps(result,indent=2)+'\n');print('SURVIVING_FOLDS',json.dumps({k:v for k,v in result.items()if k!='rows'}),flush=True)
