from pathlib import Path
import json,hashlib,datetime,ctypes,ctypes.util,struct,collections,time
b=Path('/home/hclau/ecdsa_research');r=b/'n2-temporal-storage-20261016';r.mkdir(exist_ok=True);e=b/'current-value-attribution-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();N=2**64-1;began=time.time()
family_path=e/'n2-loan-family.json';markers_path=e/'actual-loan-markers.json';prefix_path=b/'n2-readonly-normalizers-20261016/RESULT.json';ops_path=b/'product-exact-20261015/tip/ops.bin'
family=json.loads(family_path.read_text());markers=json.loads(markers_path.read_text());prefix=json.loads(prefix_path.read_text());assert family['actual_stream_sha256']==prefix['stream_sha256']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
phases=[];excluded=set();all_targets=[]
for f in family['families']:
 targets=[q for rail in f['source_rails_bit1through5']for q in rail[:4]];assert len(targets)==8;excluded.update(targets);all_targets.extend(targets)
 zeros=[q['target']for p in prefix['phases']if p['phase']==f['phase']for q in p['queries']if q['dirty_atom_count']==0 and not q['constant']];assert len(zeros)==2;nonconstant=[q for q in targets if q not in zeros];assert len(nonconstant)==6
 phases.append(dict(phase=f['phase'],full_start=f['out_span'][0],after_out=f['out_span'][1],before_in=f['returned_span'][0],full_end=f['returned_span'][1],all8source_slots=targets,prefix_exact_zero_slots=zeros,separate6_nonconstant_slots=nonconstant))
for m in markers['markers']:
 if m['label']=='in-after':excluded.update(m['rail0'][:4]);excluded.update(m['rail1'][:4])
assert len(phases)==2 and len(all_targets)==16
declaration=dict(status='FIXED ALL-SOURCE TEMPORAL ZERO-HOLE CAPACITY AUDIT BEFORE SCAN',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),stream_sha256=family['actual_stream_sha256'],all2source_loans_all16slots=True,phases=phases,excluded_original_and_returned_loan_slots=sorted(excluded),zero_hole_rule='A hole starts only immediately after an unconditional depth0/no-direct-condition R or HMR. It ends before EVERY next physical quantum read/write/phase/metadata use, regardless of guard. No assumed initial zero or propagation across reads.',capacity_queries='Complete full loan and optimistic after-out→before-in corridor. Count capacity≥6 and≥8 epochs, first possible6point, all slot first touches/MR.',scope='Six separate nonconstant slots per phase, not a proof of six independent information bits; correlations/compression unanalysed. Dirty-compatible arithmetic before first bank requires separate proof.',limits=dict(threads=1,address_space_GiB=16,time_seconds=300),no_candidate=True,no_sampling=True,no_rewrite=True,inputs={str(p):sha(p)for p in[family_path,markers_path,prefix_path,ops_path]})
p=r/'PREDECLARATION.json';assert not p.exists();p.write_text(json.dumps(declaration,indent=2)+'\n');assert declaration['inputs'][str(ops_path)]==declaration['stream_sha256']
data=ops_path.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0];z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;buf=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(buf,len(buf),data[16:],len(data)-16)==n*56;del data
limit=max(p['full_end']for p in phases);open_hole=[None]*1234;holes=[];depth=0;first={(p['phase'],q):{}for p in phases for q in p['all8source_slots']};reset_count=0
def close(q,at,kind):
 old=open_hole[q]
 if old is not None:
  start,proof=old
  if start<at and any(start<p['full_end']and at>p['full_start']for p in phases):holes.append(dict(q=q,start=start,end=at,unconditional_zero_MR=proof,next_touch_at=at,next_touch_kind=kind))
  open_hole[q]=None
for at in range(limit):
 o=struct.unpack_from('<7Q',buf,at*56);k,c2,c1,t,bt,cc,reg=o;touch={q for q in[c2,c1,t]if q!=N}
 for q in touch:
  assert q<1234
  if q not in excluded:close(q,at,k)
 for p in phases:
  if p['after_out']<=at<p['before_in']:
   for q in p['all8source_slots']:
    f=first[(p['phase'],q)]
    if q in touch and 'first_any_touch'not in f:f['first_any_touch']=dict(at=at,fields=list(o))
    if k in[11,12]and t==q and 'first_MR'not in f:f['first_MR']=dict(at=at,fields=list(o),unconditional=(depth==0 and cc==N))
 if k in[11,12]and depth==0 and cc==N and t not in excluded:open_hole[t]=(at+1,dict(at=at,kind=k,fields=list(o)));reset_count+=1
 if k==15:depth+=1
 elif k==16:depth-=1;assert depth>=0
for q in range(1234):
 if q not in excluded:close(q,limit,None)
def capacity(start,end,hh):
 events=collections.defaultdict(int);events[start]+=0;events[end]+=0
 for h in hh:
  a=max(start,h['start']);c=min(end,h['end'])
  if a<c:events[a]+=1;events[c]-=1
 points=sorted(events);count=0;segments=[]
 for a,c in zip(points,points[1:]):
  count+=events[a]
  if a<c:segments.append([a,c,count])
 def epochs(threshold,high):
  out=[]
  for a,c,n in segments:
   if (n>=threshold)==high:
    if out and out[-1][1]==a:out[-1][1]=c
    else:out.append([a,c])
  return out
 high6=epochs(6,True);low6=epochs(6,False);first6=high6[0][0]if high6 else None
 bank=[h for h in hh if first6 is not None and h['start']<=first6<h['end']]
 return dict(start=start,end=end,minimum=min(x[2]for x in segments),maximum=max(x[2]for x in segments),capacity_weighted_op_mean=sum((c-a)*n for a,c,n in segments)/(end-start),all_boundaries_capacity_at_least6=not low6,first_possible6_separate_slot_bank_boundary=first6,first6_bank_all_available_holes=bank,epochs_at_least6=high6,epochs_below6=low6,epochs_at_least8=epochs(8,True),segments=segments)
out=[]
for p in phases:
 hh=[h for h in holes if h['start']<p['full_end']and h['end']>p['full_start']];full=capacity(p['full_start'],p['full_end'],hh);core=capacity(p['after_out'],p['before_in'],hh);f=[dict(q=q,prefix_exact_zero=q in p['prefix_exact_zero_slots'],**first[(p['phase'],q)])for q in p['all8source_slots']];first_touch=min(x['first_any_touch']['at']for x in f if not x['prefix_exact_zero']);first_mr=min(x['first_MR']['at']for x in f if not x['prefix_exact_zero']);first_bank=core['first_possible6_separate_slot_bank_boundary']
 out.append(dict(**p,holes=hh,full_capacity=full,optimistic_core_capacity=core,all8slot_first_events=f,earliest_nonconstant_slot_touch=first_touch,earliest_nonconstant_slot_MR=first_mr,first6_bank_before_first_nonconstant_touch=first_bank is not None and first_bank<=first_touch,first6_bank_before_first_nonconstant_MR=first_bank is not None and first_bank<=first_mr))
for p,h in declaration['inputs'].items():assert sha(Path(p))==h,'before/after input pin'
result=dict(status='TERMINAL SOURCE-ONLY STRICT TEMPORAL CAPACITY AUDIT',declaration_sha256=sha(r/'PREDECLARATION.json'),inputs_before_after_identical=True,zero_holes_only_after_unconditional_MR=True,every_q_read_write_phase_use_is_fence=True,all_loan_slots_excluded=True,unconditional_MR_starts_scanned=reset_count,phases=out,no_candidate_or_sample=True,no_arithmetic_or_profit_claim=True,six_slots_not_an_information_theoretic_lower_bound=True,seconds=time.time()-began)
(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='phases'},indent=2))
for p in out:
 print(json.dumps(dict(phase=p['phase'],min_full=p['full_capacity']['minimum'],min_core=p['optimistic_core_capacity']['minimum'],max_core=p['optimistic_core_capacity']['maximum'],first6=p['optimistic_core_capacity']['first_possible6_separate_slot_bank_boundary'],first_touch=p['earliest_nonconstant_slot_touch'],first_MR=p['earliest_nonconstant_slot_MR'],core_below6_epochs=len(p['optimistic_core_capacity']['epochs_below6']),all_core6=p['optimistic_core_capacity']['all_boundaries_capacity_at_least6'])))
