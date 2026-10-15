from pathlib import Path
import array,ctypes as c,hashlib,json,struct,time,collections
root=Path(__file__).resolve().parent;plan=json.loads((root/'DECLARATION.json').read_text());source=Path(plan['stream']);blob=source.read_bytes();assert hashlib.sha256(blob).hexdigest()==plan['stream_sha256'];assert blob[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',blob,8)[0]
lib=c.CDLL('libzstd.so.1');lib.ZSTD_decompress.argtypes=[c.c_void_p,c.c_size_t,c.c_void_p,c.c_size_t];lib.ZSTD_decompress.restype=c.c_size_t;lib.ZSTD_isError.argtypes=[c.c_size_t];lib.ZSTD_isError.restype=c.c_uint
raw=c.create_string_buffer(n*56);compressed=blob[16:];size=lib.ZSTD_decompress(raw,len(raw),compressed,len(compressed));assert not lib.ZSTD_isError(size) and size==n*56
N=(1<<64)-1;versions=collections.defaultdict(int);qwrite=collections.defaultdict(int);pending={};stack=[];proposals=[];counts=collections.Counter();rejections=collections.Counter();began=time.monotonic()
def invalidate(q):
 if q!=N:pending.pop(q,None)
for at,(kind,b,a,t,bt,cc,reg) in enumerate(struct.iter_unpack('<7Q',raw)):
 counts[kind]+=1
 if kind in [1,2,15,16,17]:
  pending.clear()
  if kind==15:stack.append((at,cc,versions[cc]))
  elif kind==16:stack.pop()
  continue
 guard=tuple((s[1],s[2]) for s in stack)+(() if cc==N else ((cc,versions[cc]),))
 if kind==13:
  prior=pending.get(t)
  if prior is not None:
   controls={a,b};common=controls & set(prior['controls']);union=controls | set(prior['controls'])
   reason=None
   if at-prior['op']-1>64:reason='distance'
   elif guard!=prior['guard']:reason='different_guard'
   elif len(common)!=1 or len(union)!=3:reason='not_single_shared_control'
   elif any(qwrite[q]!=epoch for q,epoch in prior['epochs']):reason='old_control_written'
   elif qwrite[next(iter(controls-set(prior['controls'])))]>prior['op']:reason='new_control_written'
   if reason is None:
    shared=next(iter(common));others=sorted(union-{shared});labels=set(guard)
    proposals.append({'first':prior['op'],'second':at,'target':t,'shared':shared,'other_controls':others,'guard_value_epochs':list(guard),'structural_proxy':2.0**(-len(labels)),'source_T_delta_when_enabled':-1,'extra_CX':2})
   else:rejections[reason]+=1
  # Current controls are reads and fence other pending targets. Current target
  # is inspected first, because its second XOR update is the proposed endpoint.
  invalidate(a);invalidate(b);invalidate(t)
  qwrite[t]=at
  pending[t]={'op':at,'controls':(a,b),'epochs':((a,qwrite[a]),(b,qwrite[b])),'guard':guard}
  continue
 # Every use of the proposed target, including phase/measurement, is a fence.
 reads=[];writes=[]
 if kind in [6,7,11,12]:reads=[t]
 elif kind in [8,9,10]:reads=[a,t]
 elif kind==14:reads=[a,b,t]
 if kind in [6,8,11,12]:writes=[t]
 elif kind==10:writes=[a,t]
 for q in reads:invalidate(q)
 for q in writes:qwrite[q]=at
 if kind in [3,4,5,12]:versions[bt]+=1
assert not stack
selected=[];last_end=-1
for proposal in proposals:
 if proposal['first']>last_end:selected.append(proposal);last_end=proposal['second']
result={'status':'TERMINAL_SOURCE_ONLY_NO_REWRITE','source_sha256':plan['stream_sha256'],'operations':n,'operation_kind_counts':dict(counts),'eligible_pairs':len(proposals),'nonoverlapping_pairs':len(selected),'nonoverlapping_structural_proxy':sum(p['structural_proxy'] for p in selected),'rejections':dict(rejections),'scan_seconds':time.monotonic()-began,'sampled_inputs':0,'rewrites_applied':0,'candidate_created':False,'selection':selected}
(root/'proposals.jsonl').write_text(''.join(json.dumps(p,sort_keys=True)+'\n' for p in proposals));(root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='selection'},indent=2))
