from pathlib import Path
import json,struct,hashlib,ctypes,ctypes.util,collections,time
b=Path('/home/hclau/ecdsa_research');r=b/'census-deletion-n2-join-20261016';r.mkdir(exist_ok=True);N=2**64-1;start=time.monotonic();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[b/'payload-model-20261016/before-census.bin',b/'product-exact-20261015/tip/ops.bin',b/'census-deletion-family-20261016/ALL74.json',b/'census-control-review-20261016/ALL144.json',b/'current-value-attribution-20261016/actual-add-markers.json',b/'current-value-attribution-20261016/actual-loan-markers.json',b/'current-value-attribution-20261016/actual-markers.json']
pins={str(p):sha(p)for p in paths};assert pins[str(paths[0])]=='4b603d502456f8db2145ac5f7c36c9b44f496acfd0c3c5cc3149006cbc51a310';assert pins[str(paths[1])]=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
assert not (r/'PREDECLARATION.json').exists();(r/'PREDECLARATION.json').write_text(json.dumps(dict(family='All74 deletions, all2 N2loans/all16 slots and all786 lowadd source instances',inputs=pins,budget=dict(threads=1,GiB=16,seconds=300),method='Distinct Boolean reachability tag per restored deletion; virtual ALL74 retained, ALL70 reductions retained; no circuit emission. Conservative union ignores cancellations. Only known-active resets kill tags. Conditional branches union possibilities.',no_sampling=True,no_candidate=True,no_actual_repair_claim=True),indent=2)+'\n')
d=paths[0].read_bytes();n=struct.unpack_from('<Q',d,8)[0];z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),d[16:],len(d)-16)==n*56;raw=out.raw;del out,d
all74=json.loads(paths[2].read_text());rows=json.loads(paths[3].read_text());assert len(all74)==74;events={e['raw_index']:(i,e)for i,e in enumerate(all74)};replace={e['raw_index']:tuple(e['new'])for e in rows if e['new']is not None}
addons=json.loads(paths[4].read_text());loans=json.loads(paths[5].read_text());mark=json.loads(paths[6].read_text());queries=collections.defaultdict(list)
for source,data in [('add',addons),('loan',loans)]:
 assert data['actual_stream_sha256']==pins[str(paths[1])]
 for m in data['markers']:queries[m['anchor']['actual_at']].append((source,m))
assert len(addons['markers'])==1572 and len(loans['markers'])==8
inputs=set(o[4]for o in struct.iter_unpack('<7Q',raw)if o[0]==2 and o[4]!=N);cv={v:None for v in inputs};stack=[];guard=1;q=[0]*1234;deleted=0;results={};scope_stack=[];scope_map={};both=lambda a,b:0 if a==0 or b==0 else 1 if a==b==1 else None
def snapshot(actual_at):
 for family,m in queries.get(actual_at,[]):
  key=family+':'+str(m['id'])+':'+str(m.get('before',m.get('label')));rec={k:v for k,v in m.items()if k in ['id','phase','tick','rev','before','label']};rec.update(actual_at=actual_at,tagged_wires={})
  fields=['b','acc','carry'] if family=='add' else ['rail0','rail1']
  for field in fields:
   wires=m.get(field);wires=[] if wires is None else [wires]if isinstance(wires,int)else wires;rec['tagged_wires'][field]=[dict(q=wire,tag_mask=hex(q[wire]))for wire in wires if q[wire]]
  if family=='loan':rec['fixed_all_loan_slot_tags']={str(wire):hex(q[wire])for wire in sorted(set(w for lm in loans['markers']for f in ['rail0','rail1']for w in lm.get(f,[])))}
  results[key]=rec
for at,original in enumerate(struct.iter_unpack('<7Q',raw)):
 actual_at=at-deleted;snapshot(actual_at);o=replace.get(at,original);k,c2,c1,t,bt,cc,reg=o
 if k==15:stack.append(guard);guard=both(guard,cv.get(cc,0));scope_stack.append(at);continue
 if k==16:
  begin=scope_stack.pop();scope_map[begin]=at+1;guard=stack.pop();continue
 active=both(guard,1 if cc==N else cv.get(cc,0))
 if at in events:
  i,e=events[at];assert tuple(e['old'])==o;e['join_enclosing_push_raw_starts']=scope_stack[:]
  if active!=0:q[t]|=1<<i
  deleted+=1
 if active!=0:
  if k==8:q[t]|=q[c1]
  elif k==13:q[t]|=q[c1]|q[c2]
  elif k==10:
   if active==1:q[t],q[c1]=q[c1],q[t]
   else:q[t]=q[c1]=q[t]|q[c1]
  elif k in (11,12) and active==1:q[t]=0
  if k in (3,4,5,12):
   old=cv.get(bt,0);new=None if k==12 else (None if old is None else 1-old) if k==3 else int(k==5);cv[bt]=new if active==1 or new==old else None
assert deleted==74 and not stack and len(results)==1580
# Existing N2 markers retain exact pre-release and post-release states; all rows kept.
def source_ids(mask):return [e['source_row_one_based']for i,e in enumerate(all74)if mask>>i&1]
for rec in results.values():
 masks=[int(x['tag_mask'],16)for vs in rec['tagged_wires'].values()for x in vs];total=0
 for mask in masks:total|=mask
 rec['potential_upstream_source_rows']=source_ids(total)
 if 'fixed_all_loan_slot_tags'in rec:rec['fixed_all_loan_slot_source_rows']={wire:source_ids(int(mask,16))for wire,mask in rec['fixed_all_loan_slot_tags'].items()}
for e in all74:e['join_enclosing_balanced_raw_scopes']=[[lo,scope_map[lo]]for lo in e['join_enclosing_push_raw_starts']]
loan_results=[v for k,v in results.items()if k.startswith('loan:')];out_div=next(v for v in loan_results if v['phase']=='divide'and v['label']=='out-before');out_mul=next(v for v in loan_results if v['phase']=='multiply'and v['label']=='out-before')
unknown=[e for e in all74 if e['source_helper_label_status'].startswith('UNKNOWN')];group=collections.Counter('smallest-balanced-Push'if e['join_enclosing_balanced_raw_scopes']else'no-enclosing-syntactic-Push-helper-UNKNOWN'for e in unknown)
summary=dict(status='PASS CONSERVATIVE SOURCE-ONLY ALL74 N2/ALL786 ADD JOIN',rows=74,all_add_instances=786,add_boundary_queries=1572,loan_boundary_queries=8,all_source_rows_preserved=True,divide_out_before_all_rail_potential_sources=out_div['potential_upstream_source_rows'],divide_out_before_q555_q556_potential_sources={wire:out_div['fixed_all_loan_slot_source_rows'][wire]for wire in ['555','556']},multiply_out_before_all_rail_potential_sources=out_mul['potential_upstream_source_rows'],unknown40_syntactic_scope_grouping=dict(group),limits=['Reachability overapproximates value differences: no cancellation, zero-AND or correlated-guard reasoning. No demonstrated repair or nonzero effect.','Only value dependencies: fixed-tape HMR outcome is independent fresh input, so no quantum-to-classical tag propagation. Phase is outside this analysis.','Conditional resets retain old tags; known-active resets remove them. Paths never cross a known-active quantum reset of their carrier.','Queries at deletion-tied boundaries conservatively include all deletions before the preserved actual next Op.','A balanced Push scope is a syntactic region, not a named source helper. Unmarked depth0 helper families remain UNKNOWN.'],seconds=time.monotonic()-start)
assert time.monotonic()-start<300 and pins=={str(p):sha(p)for p in paths}
(r/'ALL74-JOIN-SOURCES.json').write_text(json.dumps(all74,indent=2)+'\n');(r/'ALL-BOUNDARIES.json').write_text(json.dumps(results,indent=2)+'\n');(r/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');(r/'INPUT-PINS.json').write_text(json.dumps(dict(before=pins,after=pins),indent=2)+'\n');print(json.dumps(summary,indent=2))
