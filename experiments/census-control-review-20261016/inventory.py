from pathlib import Path
import ctypes as c,hashlib,json,struct,collections,fractions,bisect,time
root=Path(__file__).resolve().parent;base=root.parent;inputs=root/'inputs';N=(1<<64)-1;begin=time.monotonic()
source_files={name:base/'current-value-attribution-20261016/source-observer/src/point_add'/name for name in ['census_cut_data.txt','census_anchors.txt','census_anchored.rs','census_cut.rs']}
source_files.update({'actual-markers.json':base/'current-value-attribution-20261016/actual-markers.json','FAMILY-A.json':base/'precision-family-20261016/FAMILY-A.json'})
inputs.mkdir(exist_ok=True)
for name,p in source_files.items():(inputs/name).write_bytes(p.read_bytes())
lib=c.CDLL('libzstd.so.1');lib.ZSTD_decompress.argtypes=[c.c_void_p,c.c_size_t,c.c_void_p,c.c_size_t];lib.ZSTD_decompress.restype=c.c_size_t;lib.ZSTD_isError.argtypes=[c.c_size_t];lib.ZSTD_isError.restype=c.c_uint
def load(path):
 blob=path.read_bytes();assert blob[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',blob,8)[0];out=c.create_string_buffer(n*56);data=blob[16:];size=lib.ZSTD_decompress(out,len(out),data,len(data));assert not lib.ZSTD_isError(size)and size==len(out);return n,memoryview(out).cast('B'),hashlib.sha256(blob).hexdigest()
before_path=base/'payload-model-20261016/before-census.bin';actual_path=base/'product-exact-20261015/tip/ops.bin';bn,raw,bhash=load(before_path);an,actual,ahash=load(actual_path);assert ahash=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
rows=[s.split()for s in(inputs/'census_cut_data.txt').read_text().splitlines()if s.strip()and not s.lstrip().startswith('#')];rows.sort(key=lambda f:int(f[0]));anchors=[s.split()for s in(inputs/'census_anchors.txt').read_text().splitlines()if s.strip()];assert len(rows)==len(anchors)==144 and all(len(f)==7 and f[1]in['ccx','ccz']for f in rows)
by_gate=collections.defaultdict(list);edits=[]
for e,(f,anchor)in enumerate(zip(rows,anchors)):
 old=int(f[0]);assert len(anchor)==10 and int(anchor[0])==old
 rec=(13 if f[1]=='ccx'else 14,int(f[2]),int(f[3]),int(f[4]),N,N if f[5]=='-'else int(f[5]),N);assert tuple(map(int,anchor[3:]))==rec
 gate=struct.pack('<7Q',*rec);by_gate[gate].append(e);edits.append({'row':e,'legacy_index':old,'radius':int(anchor[1]),'anchor_sha3':anchor[2],'old':rec,'action':f[6],'hits':[]})
# Independent exhaustive content-anchor uniqueness check, not a fixed offset.
classical_inputs=set()
for at in range(bn):
 recbytes=bytes(raw[at*56:(at+1)*56]);kind=recbytes[0]
 if kind==2:
  record=struct.unpack('<7Q',recbytes)
  if record[4]!=N:classical_inputs.add(record[4])
 for e in by_gate.get(recbytes,[]):
  item=edits[e];k=item['radius']
  if at>=k and at+k<bn and hashlib.sha3_256(raw[(at-k)*56:(at+k+1)*56]).hexdigest()==item['anchor_sha3']:item['hits'].append(at)
assert all(len(e['hits'])==1 for e in edits)
for e in edits:e['raw_index']=e['hits'][0]
assert all(a['raw_index']<b['raw_index']for a,b in zip(edits,edits[1:]));deleted=0
for e in edits:
 e['actual_index']=e['raw_index']-deleted;old=e['old'];action=e['action']
 if action=='del':e['new']=None;deleted+=1
 elif action.startswith('cx:'):
  keep=int(action.split(':')[1]);assert old[0]==13 and keep in old[1:3];e['new']=(8,N,keep,old[3],N,old[5],N);e['removed_control']=next(q for q in old[1:3]if q!=keep)
 elif action.startswith('cz:'):
  a,b=map(int,action.split(':')[1].split(','));assert old[0]==14 and a!=b and{a,b}<set(old[1:4]);e['new']=(9,N,a,b,N,old[5],N);e['removed_control']=next(iter(set(old[1:4])-{a,b}))
 else:raise AssertionError(action)
assert deleted==74 and sum(e['new']is not None for e in edits)==70 and bn-deleted==an
# Compare every untouched span and every replacement to actual final bytes.
previous=0;cursor=0
for e in edits:
 pos=e['raw_index'];size=(pos-previous)*56;assert raw[previous*56:pos*56]==actual[cursor*56:cursor*56+size],('unchanged',e['row']);cursor+=pos-previous
 if e['new']is not None:assert struct.pack('<7Q',*e['new'])==bytes(actual[cursor*56:(cursor+1)*56]),('replacement',e['row']);cursor+=1
 previous=pos+1
assert raw[previous*56:]==actual[cursor*56:];assert cursor+(bn-previous)==an
# All tail records are also compared above. Independently validate96 XX tail.
for at in range(an-96,an,2):
 a=bytes(actual[at*56:(at+1)*56]);b=bytes(actual[(at+1)*56:(at+2)*56]);record=struct.unpack('<7Q',a);assert a==b and record[0]==6 and record[5]==N
binding={'status':'ALL144_UNIQUE_ANCHORS_AND_ENTIRE_FINAL_CANONICAL_STREAM_EXACT','before_source_sha256':bhash,'final_source_sha256':ahash,'before_ops':bn,'final_ops':an,'all_rows':144,'deleted':74,'reduced':70,'moved_anchors':sum(e['raw_index']!=e['legacy_index']for e in edits),'entire_tail_also_equal':True,'canonical_final_sha256':hashlib.sha256(actual).hexdigest(),'canonical_pretail_sha256':hashlib.sha256(actual[:-96*56]).hexdigest()};(root/'RAW-ACTUAL-BINDING.json').write_text(json.dumps(binding,indent=2)+'\n')
# Static contexts plus independent conservative constant-only classical replay.
values={b:None for b in classical_inputs};stack=[];base_condition=1;current_edits={e['raw_index']:e for e in edits}
def get(b):return values.get(b,0)
def both(a,b):return 0 if a==0 or b==0 else 1 if a==b==1 else None
for at,(kind,b,a,t,bt,cc,reg)in enumerate(struct.iter_unpack('<7Q',raw)):
 if kind==15:stack.append(base_condition);base_condition=both(base_condition,get(cc));continue
 if kind==16:base_condition=stack.pop();continue
 enabled=both(base_condition,1 if cc==N else get(cc))
 if at in current_edits:
  e=current_edits[at];e['depth']=len(stack);e['direct_condition']=None if cc==N else cc;e['weight_exponent']=len(stack)+int(cc!=N);e['depth_weight_exact']=str(fractions.Fraction(1,1<<e['weight_exponent']));e['guard_constant_proof']=enabled
 if kind in [3,4,5,12]:
  old=get(bt)
  if enabled==0:continue
  if kind==12:new=None
  elif kind==3:new=None if old is None else 1-old
  else:new=int(kind==5)
  values[bt]=new if enabled==1 else old if new==old else None
assert not stack
# Actual helper/fold nesting; UNKNOWN mappings are retained, never shifted.
marker=json.loads((inputs/'actual-markers.json').read_text());assert marker['actual_stream_sha256']==ahash
groups=collections.defaultdict(list)
for m in marker['markers']:
 if 'anchor'in m and 'actual_at'in m['anchor']:groups[(m['family'],m.get('id'),m.get('phase'),m.get('tick'),m.get('rev'),m.get('skip'))].append(m)
regions=[]
for key,ms in groups.items():
 starts=[m for m in ms if m.get('before')is True];ends=[m for m in ms if m.get('before')is False]
 if len(starts)==len(ends)==1:
  s=starts[0]['anchor']['actual_at'];end=ends[0]['anchor']['actual_at'];assert s<=end;regions.append({'family':key[0],'id':key[1],'phase':key[2],'tick':key[3],'reverse':key[4],'skip':key[5],'span':[s,end]})
family=json.loads((inputs/'FAMILY-A.json').read_text());a29=[r for r in family['records']if 100<=r['tick']<=128];assert len(a29)==29
for e in edits:
 pos=e['actual_index'];e['source_row_one_based']=e['row']+1;e['actual_regions']=[r for r in regions if r['span'][0]<=pos<r['span'][1]];e['A29_old_region_overlap_ticks']=[r['tick']for r in a29 if r['final_begin']<=pos<r['final_end']];e['seed_restoration_same_row']=(e['row']+1==11 and e['legacy_index']==619007 and pos==619000);e['prior_coverage']='seed_exact_control_restored'if e['seed_restoration_same_row']else'A29_region_overlap_semantic_coverage_not_inferred'if e['A29_old_region_overlap_ticks']else'outside_A29_regions_and_seed'
reductions=[e for e in edits if e['new']is not None];weight=sum((fractions.Fraction(e['depth_weight_exact'])for e in reductions),fractions.Fraction());all_weight=sum((fractions.Fraction(e['depth_weight_exact'])for e in edits),fractions.Fraction());assert all_weight==fractions.Fraction(259,2)
summary={'status':'COMPLETE70_SOURCE_ONLY_INVENTORY_BOUND_TO_FINAL2A','rows':70,'reduction_kinds':dict(collections.Counter(str(e['old'][0])+'->'+str(e['new'][0])for e in reductions)),'restoration_depth_weight_exact':str(weight),'restoration_depth_weight_decimal':float(weight),'all144_depth_weight_exact':str(all_weight),'guard_constant_counts':dict(collections.Counter(str(e['guard_constant_proof'])for e in reductions)),'universal_added_executed_T_bounds':[sum(e['guard_constant_proof']==1 for e in reductions),sum(e['guard_constant_proof']!=0 for e in reductions)],'static_depth_weight_is_fresh_expected_T':False,'outside_A29_and_seed':sum(e['prior_coverage']=='outside_A29_regions_and_seed'for e in reductions),'seed_same_row':sum(e['seed_restoration_same_row']for e in reductions),'A29_region_overlap_rows':sum(bool(e['A29_old_region_overlap_ticks'])for e in reductions),'scope_depths':dict(collections.Counter(e['depth']for e in reductions)),'no_candidate':True,'no_sampling':True,'elapsed_seconds':time.monotonic()-begin};(root/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');(root/'ALL144.json').write_text(json.dumps(edits,indent=2)+'\n');(root/'ALL70.json').write_text(json.dumps(reductions,indent=2)+'\n')
pins={str(p):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for p in [*source_files.values(),before_path,actual_path]};(root/'INPUT-BINDINGS.json').write_text(json.dumps(pins,indent=2)+'\n');print(json.dumps(binding,indent=2));print(json.dumps(summary,indent=2))
