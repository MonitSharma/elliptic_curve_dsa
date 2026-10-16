from pathlib import Path
import json,struct,ctypes,ctypes.util,hashlib,collections,time,sys
from fractions import Fraction
from classical_guards import ClassicalGuards,tests
sys.setrecursionlimit(20000)
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016');inventory=json.loads((r/'source-inventory.json').read_text());NONE=2**64-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),d[16:],len(d)-16)==n*56;return out.raw
rawpath=r.parent/'free-borrow-family-20261016/raw-builder.bin';finalpath=r.parent/'product-exact-20261015/tip/ops.bin';raw=load(rawpath);final=load(finalpath);entries=[];needed=set()
assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==inventory['raw_stream_sha256']
def xrow(q):return struct.pack('<7Q',6,NONE,NONE,q,NONE,NONE,NONE)
for ident,meta in enumerate(inventory['rows']):
 s=dict(meta,id=ident);at=meta['raw_at'];prefix=b''.join(xrow(q)for q in meta['u']);s['body_parse_status']='unresolved'
 if not raw.startswith(prefix,at*56):s['body_parse_status']='source alias/early-template shape';entries.append(s);continue
 tail=raw.find(prefix,(at+len(meta['u']))*56,min(len(raw),(at+2000)*56))
 if tail<0 or tail%56:s['body_parse_status']='source tail missing';entries.append(s);continue
 end=tail//56+len(meta['u']);body=raw[at*56:end*56];ops=list(struct.iter_unpack('<7Q',body));s['raw_body_end']=end;s['body_parse_status']='complete_source_compare';s['body_sha256']=hashlib.sha256(body).hexdigest();s['body_toffoli']=sum(o[0]in[13,14]for o in ops);s['body_mr']=sum(o[0]in[11,12]for o in ops)
 s['_body']=body;s['_key']=tuple(meta['u'][:2]);needed.add(s['_key']);s['wrapper_hmr_borrow_available']=False
 if at>=2:
  h,p=struct.unpack_from('<7Q',raw,(at-2)*56),struct.unpack_from('<7Q',raw,(at-1)*56);after=struct.unpack_from('<7Q',raw,end*56)
  if h[0]==12 and p[0]==15 and p[5]==h[4]and after[0]==16:
   used={v for o in ops for v in o[1:4]if v!=NONE};s['wrapper_hmr_borrow_available']=h[3]not in used;s['borrow_target']=h[3];s['_wrapper']=raw[(at-2)*56:(end+1)*56]
 frame=s['full_operand_frame'];s['lower_frame_bound']=bool(frame and frame['lo']>=1);s['seed_source_rule_bound']=bool(frame and frame['lo']>=1 and(s['borrow']is None or s['borrow']==frame['b'][frame['lo']-1]and frame['lo']>=2))
 entries.append(s)
print('SOURCE_BODIES',collections.Counter(e['body_parse_status']for e in entries),flush=True)
positions=collections.defaultdict(list);prev=None;maxbit=0;abi=set()
for at,o in enumerate(struct.iter_unpack('<7Q',final)):
 k,zq,a,t,bt,bc,reg=o
 for bit in[bt,bc]:
  if bit!=NONE:maxbit=max(maxbit,bit)
 if k==2 and bt!=NONE:abi.add(bt)
 if k==6 and bc==NONE:
  if prev is not None and(prev[1],t)in needed:positions[(prev[1],t)].append(prev[0])
  prev=(at,t)
 else:prev=None
assert len(abi)==512
actual=collections.defaultdict(list)
for s in entries:
 if '_body'not in s:continue
 candidates=[at for at in positions[s['_key']]if final.startswith(s['_body'],at*56)]
 if '_wrapper'in s:
  bounded=[at for at in candidates if at>=2 and final.startswith(s['_wrapper'],(at-2)*56)]
  if bounded:candidates=bounded;s['actual_wrapper_bound']=True
  else:s['actual_wrapper_bound']=False
 s['final_matches']=candidates;s['unique_source_body_match']=len(candidates)==1
 for at in candidates:actual[at].append(s['id'])
print('FINAL_BINDING',len(actual),'actual intervals;',collections.Counter(len(e.get('final_matches',[]))for e in entries),flush=True)
def scan(data,queries,label):
 state=ClassicalGuards(maxbit+1,abi);result={};start=time.time()
 for at,(k,zq,a,t,bt,bc,reg)in enumerate(struct.iter_unpack('<7Q',data)):
  if at in queries:result[at]=state.snapshot()
  state.step(k,None if bt==NONE else bt,None if bc==NONE else bc,at)
  if at and at%2000000==0:print('GUARD_PROGRESS',label,at,'defs',len(state.defs),'MR',state.mr,'seconds',round(time.time()-start,2),flush=True)
 assert not state.stack;assert len(result)==len(queries)
 print('GUARD_DONE',label,'MR',state.mr,'defs',len(state.defs),'seconds',round(time.time()-start,2),flush=True)
 return result,dict(mr=state.mr,definitions=len(state.defs),negative_and_nodes=len(state.neg_nodes),elapsed_s=time.time()-start)
rawguards,rawstats=scan(raw,{e['raw_at']for e in entries},'raw')
del raw
finalguards,finalstats=scan(final,set(actual),'final')
summary=collections.defaultdict(lambda:dict(raw_source_calls=0,raw_cost_lower=Fraction(0),raw_cost_upper=Fraction(0),actual_sites=0,actual_cost_lower=Fraction(0),actual_cost_upper=Fraction(0),exact_mr_only_guards=0,data_dependent_guards=0,opaque_mr_guards=0,immediate_borrow_target_sites=0,lower_frame_bound_sites=0,fully_bound_ordinary_interface_sites=0,raw_scope_depths=collections.Counter(),actual_scope_depths=collections.Counter(),missing_source_bodies=0))
def signature(e):return(e['family'],e['source_function'],e['source_width'])
for e in entries:
 g=rawguards[e['raw_at']];e['raw_guard']=g;s=summary[signature(e)];s['raw_source_calls']+=1;s['raw_cost_lower']+=Fraction(g['lower']);s['raw_cost_upper']+=Fraction(g['upper']);s['raw_scope_depths'][g['scope_depth']]+=1
 if not e.get('final_matches'):s['missing_source_bodies']+=1
ambiguous=[];sites=[]
for at,ids in actual.items():
 signatures={signature(entries[i])for i in ids};guard=finalguards[at];row=dict(final_at=at,source_entry_ids=ids,guard=guard,source_attributions=[dict(family=a,source_function=b,width=c)for a,b,c in sorted(signatures)])
 if len(signatures)!=1:ambiguous.append(row);continue
 key=next(iter(signatures));s=summary[key];s['actual_sites']+=1;s['actual_cost_lower']+=Fraction(guard['lower']);s['actual_cost_upper']+=Fraction(guard['upper']);s['actual_scope_depths'][guard['scope_depth']]+=1;s[{'exact':'exact_mr_only_guards','data_dependent':'data_dependent_guards','opaque_mr_correlation':'opaque_mr_guards'}[guard['kind']]]+=1
 candidates=[entries[i]for i in ids];borrow=any(e['wrapper_hmr_borrow_available']and e.get('actual_wrapper_bound')for e in candidates);lower=any(e['lower_frame_bound']and e['seed_source_rule_bound']for e in candidates);full=any(e['wrapper_hmr_borrow_available']and e.get('actual_wrapper_bound')and e['lower_frame_bound']and e['seed_source_rule_bound']and e['unique_source_body_match']for e in candidates)
 s['immediate_borrow_target_sites']+=borrow;s['lower_frame_bound_sites']+=lower;s['fully_bound_ordinary_interface_sites']+=full;row.update(immediate_borrow_target_available=borrow,lower_frame_bound=lower,full_source_interface_bound=full);sites.append(row)
rows=[]
for(family,function,width),s in sorted(summary.items()):
 for field in['raw_cost_lower','raw_cost_upper','actual_cost_lower','actual_cost_upper']:s[field+'_float']=float(s[field]);s[field]=str(s[field])
 rows.append(dict(family=family,source_function=function,source_width=width,**s))
for e in entries:
 for k in list(e):
  if k.startswith('_'):del e[k]
out=dict(status='COST PROJECTION ONLY; no candidate, no scored result and no circuit selected',original_final_stream_sha256=hashlib.sha256(finalpath.read_bytes()).hexdigest(),raw_stream_sha256=inventory['raw_stream_sha256'],all_source_comparators_included=len(entries),physical_mr_draws_including_inactive=True,no_quantum_value_simulation_needed='Protected HMR classical writes are uniform fresh outcomes independent of q; all classical bit/snapshot operations replayed exactly.',probability_model='Exact expectation only for conjunctions of distinct independent physical MR literals. ABI predicates or unresolved MR correlations receive explicit bounds; no independence invented.',added_measurements='One additional physical MR draw per admitted new quantum-MAJ borrow, including inactive conditions; no extra qubit.',structural_unit_tests=tests(),raw_guard_stats=rawstats,final_guard_stats=finalstats,ambiguous_attribution_sites=ambiguous,families=rows,actual_sites=sites,source_entries=entries)
(r/'family-cost-profile.json').write_text(json.dumps(out,indent=2)+'\n');print('PROFILE_DONE',len(rows),'family/width groups',len(sites),'unambiguous actual sites',len(ambiguous),'ambiguous',flush=True)
for row in rows:
 if row['source_width']<=19:print('FAMILY_COST',row['family'],row['source_function'],row['source_width'],'raw',row['raw_source_calls'],'actual',row['actual_sites'],'cost',row['actual_cost_lower'],row['actual_cost_upper'],'borrow',row['immediate_borrow_target_sites'],'full',row['fully_bound_ordinary_interface_sites'],flush=True)
