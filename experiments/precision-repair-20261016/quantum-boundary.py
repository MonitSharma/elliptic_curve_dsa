from pathlib import Path
import ctypes,ctypes.util,struct,json
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');none=(1<<64)-1
def rows(p):return list(struct.iter_unpack('<7Q',p.read_bytes()))
old=rows(root/'old-fold-records.bin');new=rows(root/'new-fold-records.bin')
qs=lambda r:{q for o in r for q in o[1:4]if q!=none}
added=qs(new)-qs(old)
def acc(p):
 return next(list(map(int,l.split('\t')[5].split(',')))for l in p.read_text().splitlines()if l.split('\t')[2:5]==['1','0','1'])
old_acc=acc(root/'fold-marks.tsv');new_acc=acc(root/'component/fold-marks.tsv');assert len(new_acc)==len(old_acc)+1 and new_acc[:-1]==old_acc
payload_q=new_acc[-1]
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
d=(root.parent/'product-exact-20261015/tip/ops.bin').read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;body=o.raw
site=next(r for r in json.loads((root/'surviving-folds.json').read_text())['rows']if not r['reverse']and r['tick']==1)['final_start'];last={};depth=0
for i in range(site):
 r=struct.unpack_from('<7Q',body,56*i)
 for q in r[1:4]:
  if q in added:last[q]=dict(op=i,record=r,depth=depth)
 if r[0]==15:depth+=1
 if r[0]==16:depth-=1
assert depth==0
out={}
for q in sorted(added):
 v=last.get(q);after=next(((i,r)for i,r in reversed(list(enumerate(new)))if q in r[1:4]),None)
 zero=v is None or(v['record'][0]in[11,12]and v['record'][3]==q and v['record'][5]==none and v['depth']==0)
 out[q]=dict(added_payload_bit=q==payload_q,entry_last_touch=v,entry_universally_zero=zero,new_region_last_touch=after)
(root/'quantum-boundary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
