from pathlib import Path
import json,struct,hashlib,difflib
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');source=(r/'prepare-regions.py').read_text();prefix=source[:source.index('raw=load(')];exec(prefix)
assert(r/'whole-region-admission-rejected.json').exists()
raw=load(r/'raw-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin');sites=json.loads((r/'regions.json').read_text());changes=[]
def writes(o,q):return o[0]in[6,8,11,12,13]and o[3]==q or o[0]==10 and q in[o[2],o[3]]
for j,s in enumerate(sites):
 begin,end,hmr=s['raw_begin'],s['raw_end'],s['raw_hmr'];rows=list(struct.iter_unpack('<7Q',raw[begin*56:end*56]));at=hmr-begin;depth=1;ce=at+2
 while depth:
  depth+=1 if rows[ce][0]==15 else -1 if rows[ce][0]==16 else 0;ce+=1
 component=enc(rows[at:ce]);fc=final.find(component);assert fc>=0 and fc%56==0 and final.find(component,fc+1)<0
 original_prefix=raw[begin*56:s['raw_r5_end']*56];fp=final.find(original_prefix);assert fp>=0 and fp%56==0 and final.find(original_prefix,fp+1)<0,('exact R5/source prefix missing',j)
 start=fp//56;fhmr=fc//56;stop=fhmr+end-hmr;actual=list(struct.iter_unpack('<7Q',final[start*56:stop*56]));offset=fhmr-start;prefix_len=s['raw_r5_end']-begin;assert actual[offset:]==rows[at:];depth=0
 for o in actual[prefix_len:offset]:
  assert all(not writes(o,q)for q in s['r'][235:256]),('high/next-low sum bit changed',j,o)
  assert not writes(o,s['target']),('overflow changed',j,o)
  if o[0]==15:depth+=1
  if o[0]==16:depth-=1
 assert depth==0
 cbset=set(s['cb']);assert not any(o[0]in[3,4,5,12]and o[4]in cbset for o in actual),('classical comparison operand mutated',j)
 tv_begin=offset-60;assert actual[tv_begin:offset]==rows[at-60:at];assert len(s['v'])==20
 block=rows[at:ce];first=next(i for i,o in enumerate(block)if o[0]==13);scratch=block[first][3];last=next(i for i,o in enumerate(block)if o[0]==12 and o[3]==scratch);cz=last+1
 new=[];target=s['target'];low=s['lower_q'];bit=s['lower_classical_bit']
 for i,o in enumerate(block):
  if i==2:new.extend([x(target,bit),cx(low,target,bit)])
  if i==first:new.append(cx(s['u'][0],target));o=(o[0],target if o[1]==s['u'][0]else o[1],target if o[2]==s['u'][0]else o[2],*o[3:])
  if i==cz:o=(o[0],o[1],target,*o[3:])
  if i==len(block)-1:new.extend([cx(low,target,bit),x(target,bit)])
  new.append(o)
  if i==cz:new.append(cx(s['u'][0],target))
 newwhole=actual[:offset]+new+actual[offset+len(block):];oldbytes=enc(actual);newbytes=enc(newwhole)
 (r/f'back-seam-{j}.bin').write_bytes(b'BACKSEA1'+struct.pack('<2I',len(actual),len(newwhole))+oldbytes+newbytes);save(r/f'old-component-{j}.bin',enc(block));save(r/f'new-component-{j}.bin',enc(new))
 s.update(admission='B retained actual middle',final_begin=start,final_end=stop,final_hmr=fhmr,component_offset=offset,component_end=offset+len(block),prefix_len=prefix_len,tv_load_offset=tv_begin,old_component_ops=len(block),new_component_ops=len(new),first_ccx_local=first,first_carry_phase_cz_local=cz,old_region_sha256=hashlib.sha256(oldbytes).hexdigest(),new_region_sha256=hashlib.sha256(newbytes).hexdigest(),delta_toffoli=0,delta_qubits=0,delta_mr=0,delta_ops=6,full_raw_region_byteidentical=False,exact_R5_prefix_byteidentical=True,high_sum_and_overflow_untouched_in_actual_middle=True,classical_comparison_source_immutable_in_region=True)
 diff=[dict(tag=tag,raw_start=begin+a,raw_end=begin+b,final_start=start+c,final_end=start+d,raw_rows=rows[a:b],actual_rows=actual[c:d])for tag,a,b,c,d in difflib.SequenceMatcher(None,rows,actual,autojunk=False).get_opcodes()if tag!='equal'];changes.append(dict(site=j,differences=diff))
(r/'regions-B.json').write_text(json.dumps(sites,indent=2)+'\n');(r/'inherited-middle-differences.json').write_text(json.dumps(changes,indent=2)+'\n')
out=final
for j in reversed(range(len(sites))):
 s=sites[j];blob=(r/f'back-seam-{j}.bin').read_bytes();n,m=struct.unpack_from('<2I',blob,8);out=out[:s['final_begin']*56]+blob[16+n*56:]+out[s['final_end']*56:]
save(r/'prototype.bin',out);print(json.dumps(sites,indent=2))
