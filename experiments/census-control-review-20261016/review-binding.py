from pathlib import Path
import ctypes,ctypes.util,hashlib,json,struct,collections,time
r=Path('/home/hclau/ecdsa_research/census-control-review-20261016');b=r.parent;N=2**64-1;started=time.time();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 data=p.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0];z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),data[16:],len(data)-16)==n*56;return o.raw
p=b/'payload-model-20261016/before-census.bin';q=b/'product-exact-20261015/tip/ops.bin';assert sha(p)=='4b603d502456f8db2145ac5f7c36c9b44f496acfd0c3c5cc3149006cbc51a310';assert sha(q)=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e';raw=load(p);actual=load(q);all144=json.loads((r/'ALL144.json').read_text());all70=json.loads((r/'ALL70.json').read_text());assert len(all144)==144 and len(all70)==70
assert {x['row']for x in all70}=={x['row']for x in all144 if x['new']is not None};assert sum(x['new']is None for x in all144)==74
source_rows=[x.split()for x in(b/'census-control-family-20261016/inputs/census_cut_data.txt').read_text().splitlines()if x.strip()and not x.lstrip().startswith('#')];source_rows.sort(key=lambda x:int(x[0]));assert len(source_rows)==144
for row,f in zip(all144,source_rows):
 at=row['raw_index'];k=row['radius'];assert at==int(f[0])==row['legacy_index'];assert tuple(row['old'])==struct.unpack_from('<7Q',raw,at*56);pattern=raw[(at-k)*56:(at+k+1)*56];assert hashlib.sha3_256(pattern).hexdigest()==row['anchor_sha3'];hit=raw.find(pattern);assert hit==(at-k)*56 and raw.find(pattern,hit+1)==-1,'unique full literal source anchor'
 assert f[6]==row['action']
expected=bytearray(raw)
for row in reversed(all144):
 at=row['raw_index']*56
 if row['new']is None:del expected[at:at+56]
 else:expected[at:at+56]=struct.pack('<7Q',*row['new'])
assert expected==actual,'complete independently applied144 stream including tail'
del expected
for row in all70:
 old=row['old'];new=row['new'];assert old[0]==13 and new[0]==8;assert len(set(old[1:4]))==3;assert new[2]in old[1:3];assert new[1]==N and new[3:]==old[3:];assert old[4]==N and old[6]==N;assert not row['A29_old_region_overlap_ticks'];assert tuple(new)==struct.unpack_from('<7Q',actual,row['actual_index']*56)
assert sum(x['seed_restoration_same_row']for x in all70)==1;seed=next(x for x in all70 if x['seed_restoration_same_row']);assert seed['row']==10 and seed['legacy_index']==619007 and seed['actual_index']==619000
# Independent structure/cost check; no fair-coin assumption for snapshots.
positions={x['actual_index']:x for x in all70};stack=[];contexts={};unconditional=0
for at,o in enumerate(struct.iter_unpack('<7Q',actual)):
 k,c2,c1,t,bt,cc,reg=o
 if at in positions:
  row=positions[at];assert row['depth']==len(stack);assert cc==N;contexts[at]=list(stack)
  if not stack:unconditional+=1
 if k==15:stack.append(cc)
 elif k==16:stack.pop()
assert not stack and unconditional==56;assert collections.Counter(map(len,contexts.values()))=={0:56,1:14}
# Source-only lifecycle audit: snapshots of each restored target's next value
# write and next physical MR. This diagnoses obligations; it proves no cleanup.
nq=1234;next_write=[None]*nq;next_mr=[None]*nq;life={}
for at in range(len(actual)//56-1,-1,-1):
 o=struct.unpack_from('<7Q',actual,at*56);k,c2,c1,t,bt,cc,reg=o
 if at in positions:
  row=positions[at];target=row['old'][3];life[at]=dict(next_value_write=next_write[target],next_MR=next_mr[target])
 if k in[6,8,13,11,12]:next_write[t]=dict(at=at,kind=k,fields=list(o))
 elif k==10:
  item=dict(at=at,kind=k,fields=list(o));next_write[t]=item;next_write[c1]=item
 if k in[11,12]:next_mr[t]=dict(at=at,kind=k,fields=list(o))
cases=[]
for row in all70:
 at=row['actual_index'];v=life[at];mr=v['next_MR'];stop=mr['at']if mr else len(actual)//56;deletes=[x['row']for x in all144 if x['new']is None and at<x['actual_index']<=stop]
 cases.append(dict(source_row_one_based=row['row']+1,actual_at=at,source_gate=row['old'],current_gate=row['new'],scope_snapshot_bits=contexts[at],**v,retained_deletion_rows_before_next_MR=deletes))
summary=collections.Counter(str(v['next_value_write']['kind'])if v['next_value_write']else'NONE'for v in cases)
out=dict(status='PASS INDEPENDENT144 BASELINE BINDING AND70 ELEMENTARY RESTORATION REVIEW',input_hashes={str(x):sha(x)for x in[p,q,r/'ALL144.json',r/'ALL70.json',r/'inventory.py']},all144_anchors_independently_unique_and_exact=True,entire_before144_application_equals_final_actual_bytes=True,all70_uniform_CCX_to_CX=True,all74_deletions_retained_as_separate_family=True,no_A29_overlap=True,seed_row_one_based11_verified=True,full_arbitrary_dirty_gate_contract='For any t,a,b and scope/direct guard g: target_new=t XOR(g AND a AND b), controls unchanged, no phase multiplier. Valid on arbitrary superpositions by linearity. No clean scratch premise or measurement.',unchanged_MR_classical_ABI_positions_for_future70_one_for_one_restoration=True,executed_added_T_per_shot_bounds=[56,70],syntactic_depth_weight_proxy=63,proxy_is_not_measured_expected_T=True,helper_lifecycle_next_value_write_kinds=dict(summary),helper_lifecycles=cases,limitations=['Review binds original4b family only; actual generated candidate/native bytes still require independent comparison.','Restored original gate semantics do not establish each complete helper is correct with the74deletions or other inherited approximations retained.','No whole arithmetic correctness, identical phase to original4b, or monotone failure reduction claim. Fresh paired gate remains necessary.','No candidate stream generated or serialized; source lifecycle inspection only.'],seconds=time.time()-started)
(r/'REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='helper_lifecycles'},indent=2))
