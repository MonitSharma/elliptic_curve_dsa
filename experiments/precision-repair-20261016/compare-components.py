from pathlib import Path
import ctypes,ctypes.util,struct,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
def mark(p):
 rows=[l.split('\t')for l in p.read_text().splitlines()];rows=[r for r in rows if r[3]=='0'and r[4]=='1'];assert len(rows)==2
 return {('start'if r[2]=='1'else'end'):int(r[0])for r in rows}
old=load(root/'raw-builder.bin');new=load(root/'component/raw-builder.bin');a=mark(root/'fold-marks.tsv');b=mark(root/'component/fold-marks.tsv')
prefix=old[:56*a['start']]==new[:56*b['start']];suffix=old[56*a['end']:]==new[56*b['end']:]
x=old[56*a['start']:56*a['end']];y=new[56*b['start']:56*b['end']]
record=lambda body,i:struct.unpack_from('<7Q',body,56*i)
stats=lambda body:{str(k):sum(record(body,i)[0]==k for i in range(len(body)//56))for k in [11,12,13,14,15,16]}
result=dict(old=a,new=b,old_ops=len(x)//56,new_ops=len(y)//56,prefix_byte_identical=prefix,suffix_byte_identical=suffix,old_sha256=hashlib.sha256(x).hexdigest(),new_sha256=hashlib.sha256(y).hexdigest(),old_counts=stats(x),new_counts=stats(y),source_full_context_equivalence=prefix and suffix)
(root/'component-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
assert prefix and suffix,'The source change is not isolated to the proposed complete fold region'
(root/'old-fold-records.bin').write_bytes(x);(root/'new-fold-records.bin').write_bytes(y)
