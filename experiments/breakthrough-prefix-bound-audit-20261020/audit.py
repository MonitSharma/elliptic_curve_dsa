"""Read-only exact record comparison for the first whole-stream binding stop."""
import hashlib,json,mmap,re,struct,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;source=ws/'breakthrough-prefix-tick-canonical-20261020';t=source/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((source/'SOURCE-FREEZE.json').read_text());assert(source/'run.exit').read_text().strip()=='1'and(source/'generate-control.exit').read_text().strip()=='0'and(source/'generate-mixed.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert sha(source/'control/ops.bin')==f['control_exact_public_stream_sha256'];paths={};counts={};streamhashes={}
for mode in ['control','mixed']:
 original=source/mode/'before-square_finish.ops.bin';dest=r/(mode+'.records.bin');assert not dest.exists();streamhashes[mode]=sha(original)
 with original.open('rb',buffering=0)as data,dest.open('xb')as out:
  header=data.read(16);assert header[:8]==b'QECCOPSZ';counts[mode]=int.from_bytes(header[8:],'little');p=subprocess.run(['zstd','-dc'],stdin=data,stdout=out,check=True)
 assert dest.stat().st_size==counts[mode]*56;paths[mode]=dest
with paths['control'].open('rb')as af,paths['mixed'].open('rb')as bf:
 a=mmap.mmap(af.fileno(),0,access=mmap.ACCESS_READ);b=mmap.mmap(bf.fileno(),0,access=mmap.ACCESS_READ);na,nb=counts['control'],counts['mixed'];limit=min(na,nb);block=16384
 def common(backwards):
  done=0
  def eq(n):return(a[(na-done-n)*56:(na-done)*56]==b[(nb-done-n)*56:(nb-done)*56])if backwards else(a[done*56:(done+n)*56]==b[done*56:(done+n)*56])
  while done<limit:
   size=min(block,limit-done)
   if eq(size):done+=size;continue
   low,high=0,size
   while low<high:
    mid=(low+high+1)//2
    if eq(mid):low=mid
    else:high=mid-1
   return done+low
  return done
 prefix=common(False);suffix=common(True);assert prefix+suffix<=limit;old_suffix_start=na-suffix;new_suffix_start=nb-suffix;oldhash=hashlib.sha3_256(a).hexdigest();newhash=hashlib.sha3_256(b).hexdigest();module=(t/'src/point_add/square_finish.rs').read_text();assert re.search(r'const ENABLED: bool = true;',module);expected_count=int(re.search(r'assert_eq!\(ops.len\(\),(\d+),"operation table input length"',module)[1]);expected_hash=re.search(r'=="([0-9a-f]{64})"',module)
 if expected_hash is None:expected_hash=re.search(r'\),"([0-9a-f]{64})","operation table input hash"',module)
 assert expected_count==na==11453250 and expected_hash and expected_hash[1]==oldhash
 data=(t/'src/point_add/square_finish.bin').read_bytes();ne=struct.unpack_from('<I',data)[0];flat=4+12*ne;assert flat<=len(data);edits=[];missing=[];no=(1<<64)-1
 for e in range(ne):
  old_at,first,n=struct.unpack_from('<III',data,4+12*e);assert n>=1 and flat+12*(first+n)<=len(data);expected=tuple(no if x==65535 else x for x in struct.unpack_from('<6H',data,flat+12*first))+(no,);actual=struct.unpack_from('<7Q',a,old_at*56);assert actual==expected
  if old_at<prefix:new_at=old_at;region='common_prefix'
  elif old_at>=old_suffix_start:new_at=old_at+(nb-na);region='common_suffix'
  else:missing.append({'edit':e,'old_index':old_at});continue
  assert struct.unpack_from('<7Q',b,new_at*56)==expected;replacement=data[flat+12*(first+1):flat+12*(first+n)];edits.append({'edit':e,'old_index':old_at,'new_index':new_at,'region':region,'replacement_records':n-1,'replacement_bytes_sha256':hashlib.sha256(replacement).hexdigest()})
 result={'status':'EVERY_SQUARE_FINISH_EDIT_INSIDE_EXACTLY_UNCHANGED_RECORD_REGION'if not missing else'EDIT_SUPPORT_INTERSECTS_CHANGED_REGION_DO_NOT_TRANSPORT','old_source_input_count':na,'new_source_input_count':nb,'record_index_delta':nb-na,'old_input_records_sha3':oldhash,'new_input_records_sha3':newhash,'old_compressed_input_sha256':streamhashes['control'],'new_compressed_input_sha256':streamhashes['mixed'],'common_prefix_records':prefix,'common_suffix_records':suffix,'old_common_suffix_start':old_suffix_start,'new_common_suffix_start':new_suffix_start,'common_prefix_sha3':hashlib.sha3_256(a[:prefix*56]).hexdigest(),'common_suffix_sha3':hashlib.sha3_256(a[old_suffix_start*56:]).hexdigest(),'table_edits':ne,'mapped_edits':edits,'unmapped_edits':missing,'table_sha256':sha(t/'src/point_add/square_finish.bin'),'original_module_sha256':sha(t/'src/point_add/square_finish.rs'),'source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'scope':'Exact byte/record and index audit only; control input satisfies original public module count/SHA3. No old table or assertion modified. This does NOT by itself prove arbitrary contextual rewrite validity. Any transport also requires exact native arithmetic interface/phase justification, no live-state relabeling, new whole-input binding, complete validation and final declared failure gate. No resource score or nonce screening.'};a.close();b.close()
(r/'CONTEXT-BINDING-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['mapped_edits','unmapped_edits']},indent=2));print('Unmapped edits:',len(missing));(r/'run.exit').write_text('0\n')
