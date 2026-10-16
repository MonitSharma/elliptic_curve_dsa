from pathlib import Path
import ctypes,ctypes.util,hashlib,json,struct,collections,fractions,time
b=Path('/home/hclau/ecdsa_research'); r=b/'census-deletion-family-20261016'; r.mkdir(exist_ok=True)
N=2**64-1; started=time.monotonic(); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[b/'payload-model-20261016/before-census.bin',b/'product-exact-20261015/tip/ops.bin',b/'census-control-review-20261016/ALL144.json',b/'census-control-review-20261016/census_cut_data.txt',b/'current-value-attribution-20261016/actual-markers.json',b/'current-value-attribution-20261016/actual-add-markers.json']
pins={str(p):sha(p) for p in paths}
assert pins[str(paths[0])]=='4b603d502456f8db2145ac5f7c36c9b44f496acfd0c3c5cc3149006cbc51a310'
assert pins[str(paths[1])]=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
decl=dict(family='ALL74 inherited census del actions, fixed public4b source, no witness selection',inputs=pins,work='Static cost/context and first subsequent operand uses in baseline and virtual restored view; no serialized candidate',budget=dict(threads=1,memory_GiB=16,seconds=300),no_sampling=True,no_build=True,no_mask_transfer=True,admission='Every one of the74 del rows, no exclusion or later adjustment')
assert not (r/'PREDECLARATION.json').exists(); (r/'PREDECLARATION.json').write_text(json.dumps(decl,indent=2)+'\n')
def load(p):
 d=p.read_bytes(); assert d[:8]==b'QECCOPSZ'; n=struct.unpack_from('<Q',d,8)[0]; z=ctypes.CDLL(ctypes.util.find_library('zstd')); z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]; z.ZSTD_decompress.restype=ctypes.c_size_t; out=ctypes.create_string_buffer(n*56); assert z.ZSTD_decompress(out,len(out),d[16:],len(d)-16)==n*56; return out.raw
raw=load(paths[0]); actual=load(paths[1]); rows=json.loads(paths[2].read_text()); dels=[e for e in rows if e['new'] is None]; assert len(dels)==74 and all(e['action']=='del' and e['old'][0]==13 for e in dels)
source=[s.split() for s in paths[3].read_text().splitlines() if s.strip() and not s.lstrip().startswith('#')]; source.sort(key=lambda f:int(f[0])); assert len(source)==144
cursor=prev=0
for e,f in zip(rows,source):
 at=e['raw_index']; assert at==int(f[0])==e['legacy_index'] and f[6]==e['action']; assert struct.unpack_from('<7Q',raw,at*56)==tuple(e['old']); k=e['radius']; pat=raw[(at-k)*56:(at+k+1)*56]; assert hashlib.sha3_256(pat).hexdigest()==e['anchor_sha3']; h=raw.find(pat); assert h==(at-k)*56 and raw.find(pat,h+1)==-1
 size=(at-prev)*56; assert raw[prev*56:at*56]==actual[cursor*56:cursor*56+size]; cursor+=at-prev
 if e['new'] is not None: assert actual[cursor*56:(cursor+1)*56]==struct.pack('<7Q',*e['new']); cursor+=1
 assert e['actual_index']==cursor-(e['new'] is not None); prev=at+1
assert raw[prev*56:]==actual[cursor*56:]
# Classical constant replay uses independent unknown ABI input bits and unknown fresh HMR results.
# Snapshot guards are copied values; no probabilistic independence is assumed.
inputs=set(o[4] for o in struct.iter_unpack('<7Q',raw) if o[0]==2 and o[4]!=N); vals={v:None for v in inputs}; stack=[]; scopes=[]; guard=1; query={e['raw_index']:e for e in dels}; both=lambda a,b:0 if a==0 or b==0 else 1 if a==b==1 else None
for at,o in enumerate(struct.iter_unpack('<7Q',raw)):
 k,c2,c1,t,bt,cc,reg=o
 if k==15: stack.append(guard); scopes.append(dict(push_at=at,bit=cc,snapshot=vals.get(cc,0))); guard=both(guard,vals.get(cc,0)); continue
 if k==16: guard=stack.pop(); scopes.pop(); continue
 enabled=both(guard,1 if cc==N else vals.get(cc,0))
 if at in query:
  e=query[at]; e['independent_scope_snapshots']=list(scopes); e['independent_guard_constant']=enabled; e['independent_depth']=len(stack); e['independent_direct_condition']=None if cc==N else cc
  assert e['depth']==len(stack) and e['guard_constant_proof']==enabled
 if k in (3,4,5,12) and enabled!=0:
  old=vals.get(bt,0); new=None if k==12 else (None if old is None else 1-old) if k==3 else int(k==5); vals[bt]=new if enabled==1 or new==old else None
assert not stack
# Diagnostic source labels only: exact paired marker mappings, no interpolation across UNKNOWNs.
regions=[]
for p in paths[4:]:
 m=json.loads(p.read_text()); assert m['actual_stream_sha256']==pins[str(paths[1])]; groups=collections.defaultdict(list)
 for x in m['markers']:
  if 'actual_at' in x.get('anchor',{}): groups[(x['family'],x.get('id'),x.get('phase'),x.get('tick'),x.get('rev'))].append(x)
 for key,xs in groups.items():
  starts=[x for x in xs if x.get('before') is True]; ends=[x for x in xs if x.get('before') is False]
  if len(starts)==len(ends)==1:
   lo=starts[0]['anchor']['actual_at']; hi=ends[0]['anchor']['actual_at']; regions.append(dict(family=key[0],id=key[1],phase=key[2],tick=key[3],reverse=key[4],span=[lo,hi]))
for e in dels:
 at=e['actual_index']; e['bound_source_regions_strict_interior']=[v for v in regions if v['span'][0]<at<v['span'][1]]; e['region_boundary_hits']=[v for v in regions if at in v['span']]; e['source_helper_label_status']='BOUND_MARKER_FAMILY' if e['bound_source_regions_strict_interior'] else 'UNKNOWN_NO_PAIRED_HELPER_MARKER'
# Reverse physical-use scan, including every possible guard branch. Virtual view applies
# the70 retained reductions but retains all74 CCXs; it is inspected, never emitted.
def next_uses(data,virtual):
 arrays={name:[None]*1234 for name in ('any_read','value_fanout','value_write','phase_use','MR')}; result={}; qmap=collections.defaultdict(list)
 for e in dels:qmap[e['raw_index'] if virtual else e['actual_index']].append(e)
 replacements={e['raw_index']:tuple(e['new']) for e in rows if e['new'] is not None} if virtual else {}
 def snapshot(at):
  for e in qmap.get(at,[]):result[e['row']]={role:{name:arr[q] for name,arr in arrays.items()} for role,q in zip(('control2','control1','target'),e['old'][1:4])}
 for at in range(len(data)//56-1,-1,-1):
  o=replacements.get(at) or struct.unpack_from('<7Q',data,at*56); k,c2,c1,t,bt,cc,reg=o
  if virtual:snapshot(at)
  rec=dict(at=at,kind=k,fields=list(o)); reads=[]; fan=[]; writes=[]; phases=[]
  if k in (6,8,13,11,12):writes.append(t)
  if k in (6,7,8,9,10,11,12,13,14): reads.append(t)
  if k in (8,9,10,13,14):reads.append(c1)
  if k in (13,14):reads.append(c2)
  if k in (8,13):fan.extend([c1]+([c2] if k==13 else []))
  if k==10:writes.append(c1);fan.extend([t,c1])
  if k in (7,9,14):phases=reads[:]
  for name,qs in [('any_read',reads),('value_fanout',fan),('value_write',writes),('phase_use',phases),('MR',[t] if k in (11,12) else [])]:
   for q in qs: arrays[name][q]=rec
  if not virtual:snapshot(at)
 return result
baseline=next_uses(actual,False); restored=next_uses(raw,True)
for e in dels:e['baseline_first_uses']=baseline[e['row']];e['virtual_all74_first_uses']=restored[e['row']]
weight=sum((fractions.Fraction(1,2**(e['independent_depth']+int(e['independent_direct_condition'] is not None))) for e in dels),fractions.Fraction()); lower=sum(e['independent_guard_constant']==1 for e in dels); upper=sum(e['independent_guard_constant']!=0 for e in dels)
groups=collections.Counter(); target_next=collections.Counter(); target_first=collections.Counter()
for e in dels:
 labels=sorted(set(v['family']+':'+str(v['phase'])+':'+('reverse' if v['reverse'] else 'forward') for v in e['bound_source_regions_strict_interior'])); groups['|'.join(labels) or 'UNKNOWN']+=1
 for name,out in [('value_write',target_next),('value_fanout',target_first)]:
  v=e['virtual_all74_first_uses']['target'][name];out[str(v['kind']) if v else 'NONE']+=1
summary=dict(status='PASS BOUNDED ALL74 SOURCE-ONLY INVENTORY',rows=74,kinds=dict(collections.Counter(e['old'][0] for e in dels)),scope_depths=dict(collections.Counter(e['independent_depth'] for e in dels)),classical_guard_constants=dict(collections.Counter(str(e['independent_guard_constant']) for e in dels)),rigorous_added_executed_T_per_shot_bounds=[lower,upper],syntactic_half_per_scope_proxy_exact=str(weight),proxy_not_measured_mean=True,source_marker_family_groups=dict(groups),virtual_target_next_value_write_kinds=dict(target_next),virtual_target_next_value_fanout_kinds=dict(target_first),all74_original_CCX_retained_in_virtual_view=True,all70_control_reductions_still_present_in_virtual_view=True,no_serialized_candidate=True,no_sampling=True,no_mask_transfer=True,product_margin=dict(assumed_old67_saving_T=102,conservative_remaining_after_upper_T=102-upper,conditional_only='Only in principle: fresh cache leases, native reproduction, Q and complete executed mean, fresh failure gate and new source-bound certificate all remain untested'),limits=['Unknown helper labels preserved; paired marker membership is diagnostic, not a proof of complete primitive correctness.','CCX has exact arbitrary-dirty permutation action without clean scratch; restoring it does not establish whole helper cleanup with70 reductions/other cuts retained.','No failure monotonicity or ideal arithmetic claim. Guard-dependent T bounds do not assume random independent conditions.','Fanout includes subsequent restored CCXs; first physical event is not a complete dependency or reset-cleanliness proof.'],seconds=time.monotonic()-started)
assert time.monotonic()-started<300; assert pins=={str(p):sha(p) for p in paths}
(r/'ALL74.json').write_text(json.dumps(dels,indent=2)+'\n');(r/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');(r/'INPUT-PINS.json').write_text(json.dumps(dict(before=pins,after=pins),indent=2)+'\n');print(json.dumps(summary,indent=2))
