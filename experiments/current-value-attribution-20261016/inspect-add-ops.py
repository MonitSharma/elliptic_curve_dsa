from pathlib import Path
import json,struct,ctypes,ctypes.util,collections
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016')
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
d=(r.parent/'product-exact-20261015/tip/ops.bin').read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;raw=o.raw
marks=[m for m in json.loads((r/'actual-add-markers.json').read_text())['markers']if m['id']==780];a,b=marks
alias={q:f'{name}[{i}]'for name in ['acc','b']for i,q in enumerate(a[name])}
def op(i):return struct.unpack_from('<7Q',raw,i*56)
def show(i):
 row=op(i);return dict(at=i,fields=row,aliases={str(q):alias[q]for q in row[1:4]if q in alias})
first=[show(i)for i in range(a['at'],a['at']+80)]
nonoperand={q for i in range(a['at'],a['at']+80)for q in op(i)[1:4]if q!=2**64-1 and q not in alias}
hist=collections.defaultdict(list)
for i in range(a['at']):
 row=op(i)
 if row[0] in [6,8,10,11,12,13] and row[3] in nonoperand:
  h=hist[row[3]];h.append(show(i))
  if len(h)>12:h.pop(0)
out=dict(first_add_span=[a['at'],b['at']],first80=first,nonoperand_q=sorted(nonoperand),lastwrites={str(q):hist[q]for q in sorted(nonoperand)})
(r/'tick131-first-add-ops.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
