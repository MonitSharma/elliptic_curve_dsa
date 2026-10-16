from pathlib import Path
import json,struct,ctypes,ctypes.util,hashlib,collections,time
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');N=2**64-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();assert d[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
rawpath=r/'raw-builder.bin';finalpath=r.parent/'product-exact-20261015/tip/ops.bin'
assert hashlib.sha256(rawpath.read_bytes()).hexdigest()=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69'
assert hashlib.sha256(finalpath.read_bytes()).hexdigest()=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
raw,final=load(rawpath),load(finalpath);marks=[json.loads(l)for l in(r/'raw-markers.jsonl').read_text().splitlines()];radii=[8,16,32,64,128]
ats=sorted({m['at']for m in marks});needed=set()
for at in ats:
 for radius in radii:
  if at>=radius and at+radius<=len(raw)//56:needed.add(hash(raw[(at-radius)*56:(at-radius+4)*56]))
def index(data,label):
 out=collections.defaultdict(list);start=time.time()
 for at in range(len(data)//56-3):
  key=hash(data[at*56:(at+4)*56])
  if key in needed:out[key].append(at)
 print('INDEX',label,len(out),sum(map(len,out.values())),round(time.time()-start,2),flush=True);return out
ri=index(raw,'raw');fi=index(final,'actual-final');mapping={}
for at in ats:
 trials=[];bound=None
 for radius in radii:
  if at<radius or at+radius>len(raw)//56:continue
  start=at-radius;pattern=raw[start*56:(at+radius)*56];key=hash(pattern[:4*56])
  rr=[p for p in ri.get(key,[])if raw.startswith(pattern,p*56)]
  ff=[p for p in fi.get(key,[])if final.startswith(pattern,p*56)]
  trials.append(dict(radius=radius,raw_matches=len(rr),actual_matches=len(ff)))
  if rr==[start]and len(ff)==1:
   bound=dict(actual_at=ff[0]+radius,radius=radius,literal_context_sha256=hashlib.sha256(pattern).hexdigest());break
  if rr==[start]and not ff:break # a larger centered context cannot survive
 mapping[at]=dict(raw_at=at,status='BOUND'if bound else'UNKNOWN',bound=bound,trials=trials)
# A reversed match would be a contradictory source ordering, not an admission.
good=[(at,m['bound']['actual_at'])for at,m in mapping.items()if m['bound']]
crossed=set()
for(a,b),(c,d)in zip(good,good[1:]):
 if b>d:crossed.update([a,c])
for at in crossed:mapping[at]['status']='UNKNOWN_ORDER';mapping[at]['bound']=None
pairs=collections.defaultdict(list)
for m in marks:pairs[(m['family'],m['id'])].append(m)
admitted=[];unknown=[]
for key,items in pairs.items():
 okay=all(mapping[m['at']]['bound']for m in items)
 if key[0]!='stage':okay=okay and len(items)==2 and{m['before']for m in items}=={False,True}
 if okay:
  for m in items:
   x=dict(m,raw_at=m['at']);x['at']=mapping[m['at']]['bound']['actual_at'];x['anchor']=mapping[m['at']]['bound'];admitted.append(x)
 else:unknown.append(dict(family=key[0],id=key[1],source_markers=items,reason='unmapped/ambiguous exact boundary or missing paired boundary'))
admitted.sort(key=lambda x:(x['at'],x['raw_at'],x['family'],not x.get('before',True)))
out=dict(status='ACTUAL FINAL MARKER BINDING; DIAGNOSTIC ONLY',minimum_literal_context_ops=16,
 criterion='same centered consecutive literal Op neighborhood uniquely present in raw and actual final; globally monotone; no fixed offset assumption; paired boundaries required; missing UNKNOWN',
 raw_stream_sha256=hashlib.sha256(rawpath.read_bytes()).hexdigest(),actual_stream_sha256=hashlib.sha256(finalpath.read_bytes()).hexdigest(),
 source_markers=len(marks),admitted_markers=len(admitted),unknown_regions=len(unknown),source_counts=dict(collections.Counter(m['family']for m in marks)),admitted_counts=dict(collections.Counter(m['family']for m in admitted)),
 markers=admitted,unknown=unknown,mapping=list(mapping.values()))
(r/'actual-markers.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in['markers','unknown','mapping']},indent=2))
