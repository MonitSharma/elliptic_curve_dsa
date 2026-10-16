from pathlib import Path
import json,struct,ctypes,ctypes.util,difflib,collections,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016')
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(r/'raw-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin')
marks=json.loads((r/'actual-markers.json').read_text())['markers']
out=[]
for tick in range(128,137):
 pair=sorted([m for m in marks if m['family']=='payload' and m['phase']=='divide' and m['tick']==tick and not m['rev']],key=lambda x:not x['before'])
 assert len(pair)==2
 a,b=pair;rr=[raw[i*56:(i+1)*56]for i in range(a['raw_at'],b['raw_at'])];ff=[final[i*56:(i+1)*56]for i in range(a['at'],b['at'])]
 aliases=collections.defaultdict(list)
 for side in [0,1]:
  for j,q in enumerate(a['pay'+str(side)]):aliases[q].append(f'pay{side}[{j}]')
 def decode(rec):
  row=list(struct.unpack('<7Q',rec));return dict(fields=row,aliases={str(q):aliases[q]for q in row[1:4]if q in aliases})
 edits=[]
 for kind,ra,rb,fa,fb in difflib.SequenceMatcher(None,rr,ff,autojunk=False).get_opcodes():
  if kind!='equal':edits.append(dict(kind=kind,raw_begin=a['raw_at']+ra,raw_end=a['raw_at']+rb,actual_begin=a['at']+fa,actual_end=a['at']+fb,old=[decode(x)for x in rr[ra:rb]],new=[decode(x)for x in ff[fa:fb]]))
 out.append(dict(tick=tick,raw_span=[a['raw_at'],b['raw_at']],actual_span=[a['at'],b['at']],edits=edits))
 print('TICK',tick,'spans',out[-1]['raw_span'],out[-1]['actual_span'],'edits',len(edits),'ops',sum(len(e['old'])for e in edits),sum(len(e['new'])for e in edits),flush=True)
(r/'tick128-136-raw-final-delta.json').write_text(json.dumps(dict(status='DIAGNOSTIC; no candidate change',raw_sha256=hashlib.sha256((r/'raw-builder.bin').read_bytes()).hexdigest(),final_sha256=hashlib.sha256((r.parent/'product-exact-20261015/tip/ops.bin').read_bytes()).hexdigest(),ticks=out),indent=2)+'\n')
for t in out:
 if t['tick']==131:
  for e in t['edits']:print(json.dumps(e))
