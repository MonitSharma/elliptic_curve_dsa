from pathlib import Path
import json,ast,struct,ctypes,ctypes.util,hashlib
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');NONE=2**64-1
assert(r/'raw-verification.exit').read_text().strip()=='0'
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;z.ZSTD_compressBound.argtypes=[ctypes.c_size_t];z.ZSTD_compressBound.restype=ctypes.c_size_t;z.ZSTD_compress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int];z.ZSTD_compress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),d[16:],len(d)-16)==n*56;return out.raw
def save(p,b):
 bound=z.ZSTD_compressBound(len(b));out=ctypes.create_string_buffer(bound);n=z.ZSTD_compress(out,bound,b,len(b),3);p.write_bytes(b'QECCOPSZ'+struct.pack('<Q',len(b)//56)+out.raw[:n])
def enc(rows):return b''.join(struct.pack('<7Q',*o)for o in rows)
def cx(a,t,c=NONE):return(8,NONE,a,t,NONE,c,NONE)
def x(t,c=NONE):return(6,NONE,NONE,t,NONE,c,NONE)
raw=load(r/'raw-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin');sites=[];current=None
for line in(r/'source-map.log').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='BACK_BEGIN':
  assert current is None;current=dict(raw_begin=int(f[1]),r=ast.literal_eval(f[2]),add=ast.literal_eval(f[3]),cb=ast.literal_eval(f[4]))
 elif f[0]=='BACK_R5_END':current.update(raw_r5_end=int(f[1]),ov=int(f[2]))
 elif f[0]=='BACK_COMPARE':current.update(raw_hmr=int(f[1]),target=int(f[2]),lower_q=int(f[3]),lower_classical_bit=int(f[4]),k=int(f[5]))
 elif f[0]=='BACK_END':current['raw_end']=int(f[1]);sites.append(current);current=None
assert current is None and len(sites)==2
interfaces=json.loads((r.parent/'phase-localization-20261016/source-comparator-interfaces.json').read_text());rejections=[]
for j,s in enumerate(sites):
 begin,end,hmr=s['raw_begin'],s['raw_end'],s['raw_hmr'];rows=list(struct.iter_unpack('<7Q',raw[begin*56:end*56]));at=hmr-begin;assert rows[at][0]==12 and rows[at][3]==s['ov']==s['target'];s['measurement_bit']=rows[at][4];s['raw_r5_begin']=begin+2*(len(s['r'])-257);assert s['raw_r5_end']-s['raw_r5_begin']==5616
 meta=[m for m in interfaces if m['at']==hmr+2];assert len(meta)==1;meta=meta[0];assert meta['borrow']is None and len(meta['u'])==s['k']==20;s.update(u=meta['u'],v=meta['v']);depth=1;ce=at+2
 while depth:
  depth+=1 if rows[ce][0]==15 else -1 if rows[ce][0]==16 else 0;ce+=1
 block=rows[at:ce];first=next(i for i,o in enumerate(block)if o[0]==13);scratch=block[first][3];assert set(block[first][1:3])=={s['u'][0],s['v'][0]};last=next(i for i,o in enumerate(block)if o[0]==12 and o[3]==scratch);cz=last+1;assert block[cz][0]==9 and block[cz][2:4]==(s['u'][0],s['v'][0]);assert block[-1][0]==16
 new=[];target=s['target'];low=s['lower_q'];bit=s['lower_classical_bit']
 for i,o in enumerate(block):
  if i==2:new.extend([x(target,bit),cx(low,target,bit)])
  if i==first:new.append(cx(s['u'][0],target));o=(o[0],target if o[1]==s['u'][0]else o[1],target if o[2]==s['u'][0]else o[2],*o[3:])
  if i==cz:o=(o[0],o[1],target,*o[3:])
  if i==len(block)-1:new.extend([cx(low,target,bit),x(target,bit)])
  new.append(o)
  if i==cz:new.append(cx(s['u'][0],target))
 assert len(new)==len(block)+6
 oldwhole=raw[begin*56:end*56];fa=final.find(oldwhole);full=fa>=0 and fa%56==0 and final.find(oldwhole,fa+1)<0
 if not full:
  component=enc(block);pos=final.find(component);assert pos>=0 and pos%56==0 and final.find(component,pos+1)<0
  rejections.append(dict(site=j,raw_begin=begin,raw_end=end,raw_hmr=hmr,final_hmr=pos//56,status='REJECTED whole raw back seam missing/changed/ambiguous'));continue
 s.update(final_begin=fa//56,final_end=fa//56+len(rows),final_hmr=fa//56+at,component_offset=at,component_end=ce,first_ccx_local=first,first_carry_phase_cz_local=cz,old_component_ops=len(block),new_component_ops=len(new),old_region_sha256=hashlib.sha256(oldwhole).hexdigest(),delta_toffoli=0,delta_qubits=0,delta_mr=0,delta_ops=6,full_raw_region_byteidentical=True)
 save(r/f'old-component-{j}.bin',enc(block));save(r/f'new-component-{j}.bin',enc(new));newwhole=enc(rows[:at]+new+rows[ce:]);(r/f'back-seam-{j}.bin').write_bytes(b'BACKSEA1'+struct.pack('<2I',len(rows),len(rows)+6)+oldwhole+newwhole)
(r/'regions.json').write_text(json.dumps(sites,indent=2)+'\n')
if rejections:(r/'whole-region-admission-rejected.json').write_text(json.dumps(rejections,indent=2)+'\n');raise AssertionError(rejections)
out=final
for s in reversed(sites):
 blob=(r/f'back-seam-{sites.index(s)}.bin').read_bytes();n,m=struct.unpack_from('<2I',blob,8);out=out[:s['final_begin']*56]+blob[16+n*56:]+out[s['final_end']*56:]
save(r/'prototype.bin',out);print(json.dumps(sites,indent=2))
