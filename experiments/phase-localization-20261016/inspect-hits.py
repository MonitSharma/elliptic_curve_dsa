from pathlib import Path
import json,struct,ctypes,ctypes.util,re
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016');p=r.parent/'prefilter-macro-20261016'
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(path):
 d=path.read_bytes();n=struct.unpack_from('<Q',d,8)[0];b=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(b,len(b),d[16:],len(d)-16)==n*56;return b.raw
final=load(r.parent/'product-exact-20261015/tip/ops.bin');raw=load(p/'raw-builder.bin');none=2**64-1
names=['Neg','Register','Append','BitInvert','BitStore0','BitStore1','X','Z','CX','CZ','Swap','R','HMR','CCX','CCZ','Push','Pop','Debug']
hits={}
for f in r.glob('sensitivity-*-*.jsonl'):
 for line in f.read_text().splitlines():
  row=json.loads(line)
  if row['type']=='sensitivity':hits.setdefault(row['op'],[]).append(dict(file=f.name,**row))
helpers=[];stack=[]
for line in(p/'additional/observer-complete-helpers.log').read_text().splitlines():
 fields=line.split('\t')
 if len(fields)==4 and fields[0]=='FULL_HELPER':helpers.append(dict(family=fields[1],start=int(fields[2]),end=int(fields[3])))
out=[]
for op,witnesses in sorted(hits.items()):
 anchor=final[(op-8)*56:(op+9)*56];positions=[];start=0
 while True:
  pos=raw.find(anchor,start)
  if pos<0:break
  if pos%56==0:positions.append(pos//56+8)
  start=pos+1
 ops=[]
 for i in range(max(0,op-20),op+35):
  k,b,a,t,bt,c,reg=struct.unpack_from('<7Q',final,i*56);ops.append(dict(op=i,kind=names[k],a=None if a==none else a,b=None if b==none else b,t=None if t==none else t,bt=None if bt==none else bt,c=None if c==none else c))
 containing=sorted([h for h in helpers if any(h['start']<=i<h['end']for i in positions)],key=lambda h:h['end']-h['start'])
 out.append(dict(op=op,witnesses=witnesses,raw_matches=positions,operations=ops,source_containing_helpers=containing))
(r/'sensitivity-hit-context.json').write_text(json.dumps(out,indent=2)+'\n')
for row in out:
 print('HIT',row['op'],'RAW',row['raw_matches'])
 print('SOURCE',row['source_containing_helpers'][:12])
 for op in row['operations']:print(op)
