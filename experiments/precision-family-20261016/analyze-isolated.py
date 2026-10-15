from pathlib import Path
import ctypes,ctypes.util,struct,json,hashlib,re,collections
root=Path('/home/hclau/ecdsa_research/precision-family-20261016');d=root/'isolated';none=(1<<64)-1;family=json.loads((root/'FAMILY-A.json').read_text())
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 b=p.read_bytes();n=struct.unpack_from('<Q',b,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),b[16:],len(b)-16)==n*56;return o.raw
def stats(ops):
 dep=0;native=expected=0;mr=0;qs=set();written=set();reads=set()
 for k,a,b,t,bt,bc,rt in ops:
  qs.update(v for v in[a,b,t]if v!=none)
  if k in[13,14]:native+=1;expected+=2**(-dep-int(bc!=none))
  if k in[11,12]:mr+=1
  if k in[3,4,5,12]:written.add(bt)
  if bc!=none:reads.add(bc)
  if k==3:reads.add(bt)
  if k==15:dep+=1
  if k==16:dep-=1
 assert dep==0
 return dict(native=native,expected=expected,mr=mr,quantum=sorted(qs),bits_written=sorted(written),bits_read=sorted(reads))
rows=[]
for original in family['records']:
 t=original['tick'];p=d/f'tick-{t}.new.bin'
 if not p.exists():rows.append(dict(tick=t,rejected=True,reason=(d/f'tick-{t}.rejected').read_text()if(d/f'tick-{t}.rejected').exists()else'not yet generated'));continue
 a=load(d/f'tick-{t}.old.bin');b=load(p);aa=list(struct.iter_unpack('<7Q',a));bb=list(struct.iter_unpack('<7Q',b));interface=json.loads((d/f'tick-{t}.interface.json').read_text());old=stats(aa);new=stats(bb);cp=0
 for x,y in zip(aa,bb):
  if x!=y:break
  cp+=1
 assert hashlib.sha256(a).hexdigest()==original['raw_sha256']
 payload_next=interface['acc'][56];extra=set(new['quantum'])-set(old['quantum']);active=set(interface['active_entry']);extra_scratch=extra-{payload_next};esm=(d/f'tick-{t}.esh.txt').read_text().splitlines();esh_equal=esm[0].removeprefix('OLD=')==esm[1].removeprefix('NEW=')
 rows.append(dict(tick=t,rejected=False,old_ops=len(aa),new_ops=len(bb),old=old,new=new,delta_native=new['native']-old['native'],delta_expected_component=new['expected']-old['expected'],delta_mr=new['mr']-old['mr'],common_prefix=cp,payload_next=payload_next,added_quantum=sorted(extra),added_scratch=sorted(extra_scratch),added_scratch_active_entry=sorted(extra_scratch&active),added_scratch_inactive_entry=sorted(extra_scratch-active),external_esh_equal=esh_equal,interface=interface,old_sha256=hashlib.sha256(a).hexdigest(),new_sha256=hashlib.sha256(b).hexdigest()))
summary=dict(rows=rows,generated=sum(not r['rejected']for r in rows),rejected=sum(r['rejected']for r in rows),total_delta_native=sum(r.get('delta_native',0)for r in rows),total_delta_expected_component=sum(r.get('delta_expected_component',0)for r in rows),component_only=True)
(root/'isolated-analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
print('SUMMARY',{k:v for k,v in summary.items()if k!='rows'});print('ROWS',[(r['tick'],'REJECT'if r['rejected']else(r['delta_native'],r['delta_expected_component'],r['added_scratch'],r['external_esh_equal']))for r in rows])
