from pathlib import Path
import ctypes,ctypes.util,struct,json,bisect,hashlib,re,time
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');out=root/'additional';started=time.time()
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');rows=[];marks={}
for line in(out/'observer-carry-helper.log').read_text().splitlines():
 m=re.match(r'CARRY_(\w+) at=(\d+) tick=Some\(\((true|false), (\d+)\)\)(.*)',line)
 if not m:continue
 family,at,rev,tick,tail=m.groups();key=(rev=='true',int(tick));marks.setdefault(key,{})[family]=int(at)
for (rev,tick),m in marks.items():
 if 'C6_BEGIN'not in m:continue
 for family,start,end in [('c6-through-c4-erase','C6_BEGIN','LOW_ERASE_END'),('all-recs-through-c4-erase','RECS_BEGIN','LOW_ERASE_END')]:
  rows.append(dict(family=family,reverse=rev,tick=tick,raw_begin=m[start],raw_end=m[end],admitted=False,marks=m))
lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56_many.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint64),ctypes.c_size_t];lib.anchor_find56_many.restype=ctypes.c_int
def scan(anchors,width):
 cap=256;n=len(anchors);first=(ctypes.c_uint64*n)();counts=(ctypes.c_uint32*n)();hits=(ctypes.c_uint64*(n*cap))();assert lib.anchor_find56_many(final,len(final)//56,b''.join(anchors),n,width,first,counts,hits,cap)==0
 return [list(hits[i*cap:i*cap+counts[i]])if counts[i]<=cap else None for i in range(n)]
for width in[16,8,4]:
 chosen=[r for r in rows if not r['admitted']and r['raw_end']-r['raw_begin']>=2*width]
 if not chosen:continue
 starts=scan([raw[r['raw_begin']*56:(r['raw_begin']+width)*56]for r in chosen],width);tails=scan([raw[(r['raw_end']-width)*56:r['raw_end']*56]for r in chosen],width)
 for r,aa,bb in zip(chosen,starts,tails):
  if aa is None or bb is None:continue
  n=r['raw_end']-r['raw_begin'];tol=max(64,n//4);pairs=[(a,b+width)for a in aa for b in bb if a<=b and abs(b+width-a-n)<=tol]
  if len(pairs)!=1:continue
  a,b=pairs[0];depth=0;balanced=True
  for i in range(a,b):
   k=struct.unpack_from('<Q',final,i*56)[0]
   if k==15:depth+=1
   if k==16:depth-=1
   if depth<0:balanced=False;break
  if not balanced or depth:continue
  r.update(admitted=True,final_begin=a,final_end=b,anchor_width=width,final_sha256=hashlib.sha256(final[a*56:b*56]).hexdigest())
 print('BOUND',width,sum(r['admitted']for r in rows),flush=True)
(out/'carry-helper-spans.json').write_text(json.dumps(dict(rows=rows,proof_status='DIAGNOSTIC_CANDIDATES; independent actual-final universal proof required',seconds=time.time()-started),indent=2)+'\n')
(out/'carry-helper-proof-spans.tsv').write_text(''.join(f"{r['final_begin']}\t{r['final_end']}\t{r['tick']}\t{int(r['reverse'])}\n"for r in rows if r['admitted']))
print('TICK105',json.dumps([r for r in rows if r['tick']==105]));print('TOTAL',len(rows),sum(r['admitted']for r in rows),time.time()-started)
# Find source-bound inherited-table replacements containing the opaque HMR.
target=struct.unpack_from('<7Q',final,5498416*56)[:6];tables=[]
for p in(root/'observer-tip/src/point_add').glob('*.bin'):
 d=p.read_bytes()
 if len(d)<4:continue
 ne=struct.unpack_from('<I',d)[0];flat=4+12*ne
 if flat>len(d)or(len(d)-flat)%12:continue
 for j in range(ne):
  at,first,n=struct.unpack_from('<III',d,4+12*j)
  if flat+12*(first+n)>len(d):break
  rr=[tuple((v if v!=65535 else (1<<64)-1)for v in struct.unpack_from('<6H',d,flat+12*k))for k in range(first,first+n)]
  for offset,r in enumerate(rr):
   if r[:5]==target[:5]:tables.append(dict(table=p.name,input_at=at,edit=j,row_offset=offset,exact_condition=r[5]==target[5],rows=rr))
(out/'opaque-inherited-table.json').write_text(json.dumps(dict(target=target,matches=tables),indent=2)+'\n');print('TABLE_MATCHES',[(r['table'],r['input_at'],r['row_offset'],len(r['rows']))for r in tables])
