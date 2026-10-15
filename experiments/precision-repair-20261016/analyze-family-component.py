from pathlib import Path
import ctypes,ctypes.util,struct,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');none=(1<<64)-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
def metadata(p):
 out={}
 for l in p.read_text().splitlines():
  f=l.split('\t');at,id,before,rev,t=map(int,f[:5]);r=out.setdefault((bool(rev),t),dict(reverse=bool(rev),tick=t,acc=list(map(int,f[5].split(',')))))
  r['start'if before else'end']=at
 return out
old=load(root/'raw-builder.bin');new=load(root/'family16-component/raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');om=metadata(root/'fold-marks.tsv');nm=metadata(root/'family16-component/fold-marks.tsv')
rank=json.loads((root/'PREDECLARED-FAMILY.json').read_text())['ranked_sites'][:16];version={(r['reverse'],r['tick']):r for r in json.loads((root/'version-liveness.json').read_text())['rows']};match={(r['reverse'],r['tick']):r for r in json.loads((root/'surviving-folds.json').read_text())['rows']}
rows=[];prevold=prevnew=0;gaps=[]
for selected in sorted(rank,key=lambda r:om[r['reverse'],r['tick']]['start']):
 key=selected['reverse'],selected['tick'];a=om[key];b=nm[key];x=old[56*a['start']:56*a['end']];y=new[56*b['start']:56*b['end']]
 gaps.append(old[56*prevold:56*a['start']]==new[56*prevnew:56*b['start']]);prevold=a['end'];prevnew=b['end']
 assert b['acc'][:-1]==a['acc']and len(b['acc'])==len(a['acc'])+1
 xr=list(struct.iter_unpack('<7Q',x));yr=list(struct.iter_unpack('<7Q',y));cp=0
 for u,v in zip(xr,yr):
  if u!=v:break
  cp+=1
 def incoming(rows):
  written={r[4]for r in rows if r[0]in[3,4,5,12]};initialized=set();bad=[];depth=0
  for i,r in enumerate(rows):
   reads=[r[5]]+([r[4]]if r[0]==3 else[])
   for ct in reads:
    if ct in written and ct not in initialized and i>=cp:bad.append((i,ct))
   if r[0]in[4,5,12]and r[5]==none and depth==0:initialized.add(r[4])
   if r[0]==15:depth+=1
   if r[0]==16:depth-=1
  return dict(admitted=not bad,violations=bad,unconditionally_initialized=written<=initialized)
 row=dict(**selected,old=a,new=b,shared_prefix_ops=cp,old_incoming=incoming(xr),new_incoming=incoming(yr),final_match=match[key]['found'],classical_versions=version.get(key,{}).get('classical_versions',[]),old_ops=len(xr),new_ops=len(yr),old_sha256=hashlib.sha256(x).hexdigest(),new_sha256=hashlib.sha256(y).hexdigest())
 row['outgoing_local']=bool(row['classical_versions'])and all(not v['live_out']for v in row['classical_versions']);row['incoming_common_prefix_safe']=row['old_incoming']['admitted']and row['new_incoming']['admitted']
 rows.append(row)
gaps.append(old[56*prevold:]==new[56*prevnew:])
result=dict(selected=16,outside_all_selected_regions_identical=all(gaps),gap_checks=gaps,rows=rows,component_only=True)
(root/'family16-analysis.json').write_text(json.dumps(result,indent=2)+'\n');print('FAMILY16_ISOLATION',all(gaps));print('FAMILY16_SITES',[(r['reverse'],r['tick'],r['final_match'],r['incoming_common_prefix_safe'],r['outgoing_local'],r['shared_prefix_ops'])for r in rows])
