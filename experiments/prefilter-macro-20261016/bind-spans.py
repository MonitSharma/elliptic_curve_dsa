from pathlib import Path
import ctypes,ctypes.util,struct,json,re,hashlib,difflib,collections
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');none=(1<<64)-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');entries={}
for line in(root/'observer.log').read_text().splitlines():
 m=re.match(r'MACRO_TOP1_FALSE_(BEGIN|CHAIN|COMPARE_BEGIN|COMPARE_END|END) rev=(true|false) tick=(\d+) at=(\d+)(.*)',line)
 if not m:continue
 mode,rev,t,at,tail=m.groups();e=entries.setdefault((rev=='true',int(t)),dict(reverse=rev=='true',tick=int(t)))
 e[mode.lower()]=int(at)
 if mode=='BEGIN':e['nbx'],e['bit0']=map(int,re.search(r'nbx=(\d+) bit0=(\d+)',tail).groups())
 if mode=='CHAIN':e['chain_scratch']=json.loads(tail.split('scratch=')[1])
for e in entries.values():
 a,b=e['begin'],e['end'];block=raw[56*a:56*b];assert struct.unpack_from('<Q',block,0)[0]==15
 signature=block[:56*16];at=final.find(signature);e['prefix_found']=at>=0;e['prefix_unique']=at>=0 and final.find(signature,at+56)<0
 if not e['prefix_unique']:continue
 assert at%56==0;fa=at//56;depth=0;fb=None
 for i in range(fa,min(fa+max(10000,b-a+1000),len(final)//56)):
  kind=struct.unpack_from('<Q',final,56*i)[0]
  if kind==15:depth+=1
  if kind==16:depth-=1
  assert depth>=0
  if depth==0:fb=i+1;break
 assert fb is not None
 e['final_begin'],e['final_end']=fa,fb;fblock=final[56*fa:56*fb];e['raw_ops'],e['final_ops']=b-a,fb-fa;e['raw_sha256']=hashlib.sha256(block).hexdigest();e['final_sha256']=hashlib.sha256(fblock).hexdigest();e['byte_identical']=block==fblock
 if not e['reverse']and e['tick']==3:
  old=[block[i:i+56]for i in range(0,len(block),56)];new=[fblock[i:i+56]for i in range(0,len(fblock),56)];diff=[]
  for tag,i,j,k,l in difflib.SequenceMatcher(a=old,b=new,autojunk=False).get_opcodes():
   if tag=='equal':continue
   diff.append(dict(tag=tag,raw_begin=a+i,raw_end=a+j,final_begin=fa+k,final_end=fa+l,old=[struct.unpack('<7Q',r)for r in old[i:j]],new=[struct.unpack('<7Q',r)for r in new[k:l]]))
  (root/'first-final-source-diff.json').write_text(json.dumps(diff,indent=2)+'\n')
result=dict(source_branch='y15_onefold.rs body top1 false branch: nbx & bit0; chain/CZ/cmp0/unchain',raw_component_sha256=hashlib.sha256((root/'raw-builder.bin').read_bytes()).hexdigest(),source_bound_original_final_sha256=hashlib.sha256((root.parent/'product-exact-20261015/tip/ops.bin').read_bytes()).hexdigest(),instances=len(entries),unique_prefix_bound=sum(e['prefix_unique']for e in entries.values()),whole_byte_identical=sum(e.get('byte_identical',False)for e in entries.values()),rows=list(entries.values()))
(root/'bound-spans.json').write_text(json.dumps(result,indent=2)+'\n');print('SOURCE_MACRO_BINDINGS',result['instances'],result['unique_prefix_bound'],result['whole_byte_identical']);print('FIRST',json.dumps(next(e for e in entries.values()if not e['reverse']and e['tick']==3)))
