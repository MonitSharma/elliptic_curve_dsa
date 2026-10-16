from pathlib import Path
import json,hashlib,struct,ctypes,ctypes.util,collections,time
b=Path('/home/hclau/ecdsa_research');r=b/'census-preseed-family-20261016';r.mkdir(exist_ok=True);N=2**64-1;start=time.monotonic();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[b/'payload-model-20261016/before-census.bin',b/'product-exact-20261015/tip/ops.bin',b/'census-control-review-20261016/ALL144.json',b/'census-control-review-20261016/census_cut_data.txt',b/'current-value-attribution-20261016/actual-seed-markers.json',b/'current-value-attribution-20261016/seed-region-diff.json']
pins={str(p):sha(p)for p in paths};assert pins[str(paths[0])]=='4b603d502456f8db2145ac5f7c36c9b44f496acfd0c3c5cc3149006cbc51a310';assert pins[str(paths[1])]=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
assert not(r/'PREDECLARATION.json').exists();(r/'PREDECLARATION.json').write_text(json.dumps(dict(family='ALL144 census edits STRICTLY BEFORE the exact first source mod_halve_pm/seed helper entry; complete checkpoint family, no witness subset',checkpoint=dict(actual2a_entry=618858,before_census_entry_hint=618865,older_raw_builder_entry_different=618835),inputs=pins,budget=dict(threads=1,GiB=16,seconds=300),work='Derive complete membership and scope costs; virtual in-memory restoration prefix/suffix byte proof; no serialized circuit, build, sample or mask transfer'),indent=2)+'\n')
def load(p):
 data=p.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0];z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),data[16:],len(data)-16)==len(out);return out.raw
raw=load(paths[0]);actual=load(paths[1]);rows=json.loads(paths[2].read_text());seed=json.loads(paths[4].read_text());region=json.loads(paths[5].read_text());assert region['actual_begin']==618858 and region['raw_begin']==618835;entry=next(m for m in seed['markers']if m['before']);a=entry['anchor']['actual_at'];rad=entry['anchor']['radius'];assert a==618858;pattern=actual[(a-rad)*56:(a+rad)*56];assert hashlib.sha256(pattern).hexdigest()==entry['anchor']['literal_context_sha256'];hit=raw.find(pattern);assert hit>=0 and hit%56==0 and raw.find(pattern,hit+1)==-1;before=hit//56+rad;assert before==618865;assert actual.find(pattern)==(a-rad)*56 and actual.find(pattern,(a-rad)*56+1)==-1
selected=[e for e in rows if e['raw_index']<before];remaining=[e for e in rows if e['raw_index']>=before];assert len(selected)==10 and [e['row']for e in selected]==list(range(10)) and len(remaining)==134;assert sum(e['new']is None for e in selected)==7;assert all(e['old'][0]==13 for e in selected);assert sum(e['new']is not None for e in selected)==3;assert all(e['new']is None or e['new'][0]==8 for e in selected)
source=[s.split()for s in paths[3].read_text().splitlines()if s.strip()and not s.lstrip().startswith('#')];source.sort(key=lambda f:int(f[0]));assert len(source)==144
for e,f in zip(rows,source):
 at=e['raw_index'];assert at==int(f[0])and e['action']==f[6]and struct.unpack_from('<7Q',raw,at*56)==tuple(e['old']);k=e['radius'];assert hashlib.sha3_256(raw[(at-k)*56:(at+k+1)*56]).hexdigest()==e['anchor_sha3']
stack=[];by_at={e['raw_index']:e for e in selected};scope_depth_at_entry=None
for at,o in enumerate(struct.iter_unpack('<7Q',raw[:before*56])):
 if at in by_at:
  e=by_at[at];assert not stack and o[5]==N;e['independent_depth']=0;e['independent_direct_condition']=None;e['exact_added_executed_T']=1
 if o[0]==15:stack.append(o[5])
 elif o[0]==16:stack.pop()
assert not stack
# Restore the complete prefix by applying only134 later inherited edits to the
# exact pre-census stream. No virtual stream is serialized or executed.
virtual=bytearray(raw)
for e in reversed(remaining):
 at=e['raw_index']*56
 if e['new']is None:del virtual[at:at+56]
 else:virtual[at:at+56]=struct.pack('<7Q',*e['new'])
assert virtual[:before*56]==raw[:before*56];assert virtual[before*56:]==actual[a*56:];assert len(virtual)==len(actual)+7*56
# Independently reconstruct current final2a from all144, proving every one of
# the retained134 edits has its original exact suffix action.
current=bytearray(raw)
for e in reversed(rows):
 at=e['raw_index']*56
 if e['new']is None:del current[at:at+56]
 else:current[at:at+56]=struct.pack('<7Q',*e['new'])
assert current==actual;del current
old_nonq=[o for o in struct.iter_unpack('<7Q',actual[:a*56])if o[0] not in(8,13)];new_nonq=[o for o in struct.iter_unpack('<7Q',virtual[:before*56])if o[0] not in(8,13)];assert old_nonq==new_nonq
qmax=bmax=mr=0
for k,c2,c1,t,bt,cc,reg in struct.iter_unpack('<7Q',virtual):
 for v in(c2,c1,t):
  if v!=N:qmax=max(qmax,v+1)
 for v in(bt,cc):
  if v!=N:bmax=max(bmax,v+1)
 mr+=k in(11,12)
assert(qmax,bmax,mr)==(1234,45701,906156);assert pins=={str(p):sha(p)for p in paths};assert time.monotonic()-start<300
summary=dict(status='PASS COMPLETE PRESEED10 SOURCE-ONLY CHECKPOINT FAMILY',family_count=10,selected_source_rows_one_based=[e['row']+1 for e in selected],selected_deletions=7,selected_reductions=3,remaining_rows=134,remaining_deletions=sum(e['new']is None for e in remaining),remaining_reductions=sum(e['new']is not None for e in remaining),exact_added_T_per_shot=10,added_Q_B_MR=[0,0,0],Q_B_MR=[qmax,bmax,mr],current_actual_entry=a,before_census_entry=before,older_raw_builder_seed_entry=618835,boundary_context_unique_in_both_before_and_actual=True,boundary_literal_context_sha256=hashlib.sha256(pattern).hexdigest(),prefix_ops=before,prefix_sha256=hashlib.sha256(raw[:before*56]).hexdigest(),virtual_restored_prefix_equals_before_census_prefix_byte_for_byte=True,virtual_suffix_equals_current_actual_suffix_byte_for_byte=True,suffix_old_actual_begin=a,suffix_new_virtual_begin=before,suffix_sha256=hashlib.sha256(actual[a*56:]).hexdigest(),all134_later_edits_preserved=True,virtual_ops=len(virtual)//56,virtual_canonical_sha256=hashlib.sha256(virtual).hexdigest(),classical_ABI_MR_sequence_and_physical_ids_preserved=True,old_MR_draw_ordinals_unchanged=True,suffix_Op_positions_shift_exactly7=True,scope_depth_at_checkpoint=0,no_virtual_stream_serialized=True,no_build_or_sampling=True,limits=['Prefix equality gives identical complete source-prefix action to before-census for all inputs/allMR, including phase and dirty entry. It does not establish ideal arithmetic, clean scratch, or clean N2 loans.','Remaining134 inherited census edits and all earlier non-census approximations remain; seed own row11 remains reduced.','The byte-identical suffix receives a changed quantum entry state; no full output/phase/failure monotonicity claim.','Any future cache leases, native generation, source-bound mask and sole fresh gate require new proofs; no old mask or lease transfer.'],seconds=time.monotonic()-start)
(r/'MEMBERS10.json').write_text(json.dumps(selected,indent=2)+'\n');(r/'RETAINED134.json').write_text(json.dumps(remaining,indent=2)+'\n');(r/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');(r/'INPUT-PINS.json').write_text(json.dumps(dict(before=pins,after=pins),indent=2)+'\n');print(json.dumps(summary,indent=2))
