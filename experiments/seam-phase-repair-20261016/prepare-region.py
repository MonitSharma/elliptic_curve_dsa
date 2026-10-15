from pathlib import Path
import ctypes,ctypes.util,struct,json,hashlib
r=Path('/home/hclau/ecdsa_research/seam-phase-repair-20261016');phase=r.parent/'phase-localization-20261016';none=2**64-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];b=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(b,len(b),d[16:],len(d)-16)==n*56;return b.raw
def save(path,rows):
 raw=b''.join(struct.pack('<7Q',*o)for o in rows);bound=z.ZSTD_compressBound(len(raw));out=ctypes.create_string_buffer(bound);size=z.ZSTD_compress(out,bound,raw,len(raw),3);path.write_bytes(b'QECCOPSZ'+struct.pack('<Q',len(rows))+out.raw[:size])
z.ZSTD_compressBound.argtypes=[ctypes.c_size_t];z.ZSTD_compressBound.restype=ctypes.c_size_t;z.ZSTD_compress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int];z.ZSTD_compress.restype=ctypes.c_size_t
raw=load(phase/'raw-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin');assert hashlib.sha256((phase/'raw-builder.bin').read_bytes()).hexdigest()=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69'
R=list(struct.iter_unpack('<7Q',raw[:100000*56]));interfaces=json.loads((phase/'source-comparator-interfaces.json').read_text());sites=[]
for line in(phase/'source-v2-map.log').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='PHASE_HMR'and f[4].endswith('leapfrog.rs')and int(f[5])==3983:sites.append(int(f[1]))
assert len(sites)==1;site=sites[0];meta=[m for m in interfaces if m['at']==site+2];assert len(meta)==1;meta=meta[0];u=meta['u'];v=meta['v'];assert meta['borrow']is None and u==list(range(236,256))and len(v)==20
target=R[site][3];bit=R[site][4];assert R[site][0]==12 and R[site+1][0]==15
lowq=u[0]-1;lowbit=235
depth=1;end=site+2
while depth:
 if R[end][0]==15:depth+=1
 if R[end][0]==16:depth-=1
 end+=1
block=R[site:end];first=next(i for i,o in enumerate(block)if o[0]==13);scratch=block[first][3];assert set(block[first][1:3])=={v[0],u[0]};last=next(i for i,o in enumerate(block)if o[0]==12 and o[3]==scratch);cz=last+1;assert block[cz][0]==9 and block[cz][2:4]==(u[0],v[0]);assert block[-1][0]==16
def cx(a,t,condition=none):return(8,none,a,t,none,condition,none)
new=[]
for i,o in enumerate(block):
 if i==2:new.append(cx(lowq,target,lowbit))
 if i==first:
  new.append(cx(u[0],target));o=(o[0],target if o[1]==u[0]else o[1],target if o[2]==u[0]else o[2],*o[3:])
 if i==cz:o=(o[0],o[1],target,*o[3:])
 if i==len(block)-1:new.append(cx(lowq,target,lowbit))
 new.append(o)
 if i==cz:new.append(cx(u[0],target))
assert len(new)==len(block)+4
begin=next(i for i,o in enumerate(R[:site])if o[0]in[6,8,10,11,12,13]and(o[3]<256 or o[0]==10 and o[2]<256))
assert all(R[begin+i]==(6,none,none,i,none,none,none)for i in range(256))
# Complete source seam includes operand unloads, zero resets, external X layer and ov free.
whole_end=end+5*len(u)+1
for i in range(len(u)):
 assert R[end+3*i]==(15,none,none,none,none,u[i],none)
 assert R[end+3*i+1]==(6,none,none,v[i],none,none,none)
 assert R[end+3*i+2][0]==16
assert all(R[end+3*len(u)+i][0]==11 and R[end+3*len(u)+i][3]==v[i]for i in range(len(u)))
assert all(R[end+4*len(u)+i]==(6,none,none,u[i],none,none,none)for i in range(len(u)))
assert R[whole_end-1][0]==11 and R[whole_end-1][3]==target
oldwhole=raw[begin*56:whole_end*56];found=[];pos=0
while True:
 pos=final.find(oldwhole,pos)
 if pos<0:break
 if pos%56==0:found.append(pos//56)
 pos+=1
if len(found)!=1:
 component=raw[site*56:end*56];fat=final.find(component);assert fat>=0 and fat%56==0 and final.find(component,fat+1)<0
 prefixes=[];scan=0;prefix=raw[begin*56:(begin+256)*56]
 while True:
  at=final.find(prefix,scan,fat)
  if at<0:break
  if at%56==0:prefixes.append(at)
  scan=at+1
 assert prefixes;fa=min(prefixes,key=lambda p:abs(p//56-(begin+fat//56-site)))
 fb=fat+(whole_end-site)*56;before=R[begin:whole_end];after=list(struct.iter_unpack('<7Q',final[fa:fb]));cp=0
 while cp<min(len(before),len(after))and before[cp]==after[cp]:cp+=1
 cs=0
 while cs<min(len(before),len(after))-cp and before[-1-cs]==after[-1-cs]:cs+=1
 rejection=dict(status='REJECTED complete source-front-seam byteidentity',raw_begin=begin,raw_end=whole_end,raw_hmr=site,final_begin=fa//56,final_end=fb//56,final_hmr=fat//56,common_prefix=cp,common_suffix=cs,old_middle=[dict(at=begin+cp+i,row=o)for i,o in enumerate(before[cp:len(before)-cs])],new_middle=[dict(at=fa//56+cp+i,row=o)for i,o in enumerate(after[cp:len(after)-cs])],complete_phase_helper_byteidentical=True)
 (r/'rejected-full-source-region.json').write_text(json.dumps(rejection,indent=2)+'\n');raise AssertionError(('inherited full-seam overlap/missing/ambiguous',rejection))
start=found[0];stop=start+whole_end-begin;newwhole=R[begin:site]+new+R[end:whole_end]
assert [o for o in newwhole if o[0]in[11,12]]==[o for o in R[begin:whole_end]if o[0]in[11,12]]
assert sum(o[0]in[13,14]for o in newwhole)==sum(o[0]in[13,14]for o in R[begin:whole_end])
flatnew=b''.join(struct.pack('<7Q',*o)for o in newwhole);(r/'front_seam.bin').write_bytes(b'FRONTSE1'+struct.pack('<2I',whole_end-begin,len(newwhole))+oldwhole+flatnew)
candidateraw=final[:start*56]+flatnew+final[stop*56:];bound=z.ZSTD_compressBound(len(candidateraw));out=ctypes.create_string_buffer(bound);size=z.ZSTD_compress(out,bound,candidateraw,len(candidateraw),3);(r/'prototype.bin').write_bytes(b'QECCOPSZ'+struct.pack('<Q',len(candidateraw)//56)+out.raw[:size])
save(r/'old-component.bin',block);save(r/'new-component.bin',new)
result=dict(source_primitive='leapfrog::seed_r0_seam classical-ox overflow erase',raw_begin=begin,raw_end=whole_end,raw_hmr=site,final_begin=start,final_end=stop,final_hmr=start+site-begin,old_component_ops=len(block),new_component_ops=len(new),lower_q=lowq,lower_classical_bit=lowbit,measured_and_borrow_target=target,measurement_bit=bit,u=u,v=v,first_ccx_local=first,first_carry_phase_cz_local=cz,full_old_source_region_survives_byte_identical=True,old_region_sha256=hashlib.sha256(oldwhole).hexdigest(),new_region_sha256=hashlib.sha256(flatnew).hexdigest(),delta_toffoli=0,delta_mr=0,delta_ops=4,unchanged_ops_outside_full_seam=True,all_inherited_tables_retained=True)
(r/'region.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
