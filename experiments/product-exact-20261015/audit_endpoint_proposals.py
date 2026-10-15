"""Independent byte decoder, donor isolation and local classical guard audit.

This does not prove donor zero, product equivalence, a renderer or a mean over
actual ABI inputs. Entry classical bits and internal HMR bits are arbitrary.
"""
import ast,hashlib,itertools,json,re,struct,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'endpoint-proposals-20261016';S=(1<<64)-1
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((d/'DECLARATION.json').read_text());stream=r/plan['stream'];assert sha(stream)==plan['stream_sha256']
text=(d/'analysis.log').read_text();rows=[]
for line in text.splitlines():
 m=re.fullmatch(r'LAZY_WINDOW donor=(\d+) start=(\d+) end=(\d+) proxy=([^ ]+) uses=(\[.*\])',line)
 if m:rows.append(dict(donor=int(m[1]),start=int(m[2]),end=int(m[3]),proxy=float(m[4]),uses=ast.literal_eval(m[5])))
assert len(rows)==42;rows.sort(key=lambda x:x['start']);assert all(a['end']<=b['start'] for a,b in zip(rows,rows[1:]))
ZERO=frozenset();ONE=frozenset([frozenset()])
def xor(a,b):return a^b
def mul(a,b):
 out=set()
 for x in a:
  for y in b:
   t=x|y
   if t in out:out.remove(t)
   else:out.add(t)
 assert len(out)<=1000000
 return frozenset(out)
def var(k):return frozenset([frozenset([k])])
assert mul(var('x'),xor(ONE,var('x')))==ZERO
assert mul(xor(var('x'),var('y')),xor(var('x'),var('y')))==xor(var('x'),var('y'))
def read_exact(pipe,n):
 out=bytearray()
 while len(out)<n:
  chunk=pipe.read(n-len(out));assert chunk;out.extend(chunk)
 return bytes(out)
def skip(pipe,n):
 while n:
  chunk=pipe.read(min(n,8*1024*1024));assert chunk;n-=len(chunk)
receipts=[];cursor=0
with stream.open('rb',buffering=0) as src:
 magic,n=struct.unpack('<8sQ',read_exact(src,16));assert magic==b'QECCOPSZ'
 proc=subprocess.Popen(['zstd','-dcq'],stdin=src,stdout=subprocess.PIPE)
 for row in rows:
  start,end=row['start'],row['end'];skip(proc.stdout,(start-cursor)*56);raw=read_exact(proc.stdout,(end-start)*56);cursor=end
  ops=list(struct.iter_unpack('<7Q',raw));depth=0;stack=[ONE];bits={};guards={};writes=[];resets=0;control_writes=[]
  def bit(b):
   assert b!=S
   if b not in bits:bits[b]=var(('entry',b))
   return bits[b]
  last_op=ops[row['uses'][-1]-start];assert last_op[0]==13;controls={last_op[1],last_op[2]}
  for off,op in enumerate(ops):
   at=start+off;k,b,a,t,ct,cc,reg=op
   assert 0<=k<=17
   if k==15:stack.append(mul(stack[-1],bit(cc)));depth+=1;continue
   if k==16:assert depth>0;stack.pop();depth-=1;continue
   g=stack[-1] if cc==S else mul(stack[-1],bit(cc))
   if at in row['uses']:assert k==13;guards[at]=g
   fields={q for q in (a,b,t) if q!=S}
   if row['donor'] in fields:
    assert k==11 and t==row['donor'];resets+=1
   targets={t} if k in (6,8,11,12,13) else ({a,t} if k==10 else set())
   if at>row['uses'][-1] and controls&targets:control_writes.append(at)
   if k in (3,4,5,12) and ct!=S:
    old=bit(ct)
    bits[ct]=xor(old,g) if k==3 else xor(old,mul(g,xor(old,ONE if k==5 else (var(('mr',at)) if k==12 else ZERO))))
  assert depth==0 and len(stack)==1 and len(guards)==len(row['uses']) and control_writes
  gs=[guards[i] for i in row['uses']];overlaps=[mul(a,b) for a,b in itertools.combinations(gs,2)]
  variables=sorted({v for g in gs for term in g for v in term});at_most_one=all(x==ZERO for x in overlaps)
  local_uniform_mean=None
  if len(variables)<=16:
   ids={v:i for i,v in enumerate(variables)};masks=[[sum(1<<ids[v] for v in term) for term in g] for g in gs];total=0
   for x in range(1<<len(variables)):
    active=sum(sum((x&m)==m for m in poly)%2 for poly in masks);total+=max(0,active-1)
   local_uniform_mean=total/(1<<len(variables))
  receipts.append(dict(**row,source_records_sha256=hashlib.sha256(raw).hexdigest(),source_ops=len(ops),top_level_bounds_balanced=True,old_raw_fence_rejected=True,control_write_indices=control_writes,donor_other_touches=0,donor_resets_requiring_renderer_obligation=resets,guard_variables=len(variables),guards_pairwise_disjoint_for_all_local_classical_inputs=at_most_one,independent_uniform_local_classical_gain=local_uniform_mean))
 skip(proc.stdout,(n-cursor)*56);assert not proc.stdout.read(1);assert proc.wait()==0
assert sha(stream)==plan['stream_sha256']
out=d/'INDEPENDENT_BOUNDS_DONOR_GUARDS.json';assert not out.exists()
out.write_text(json.dumps(dict(status='INDEPENDENT_SOURCE_BOUNDS_DONOR_ISOLATION_LOCAL_GUARDS_COMPLETE',stream_sha256=plan['stream_sha256'],planner_log_sha256=sha(d/'analysis.log'),audit_source_sha256=sha(Path(__file__)),leases=len(rows),all_selected_old_raw_fences_rejected=True,donor_nonreset_touches=0,donor_resets=sum(x['donor_resets_requiring_renderer_obligation'] for x in receipts),universally_local_zero_gain_leases=sum(x['guards_pairwise_disjoint_for_all_local_classical_inputs'] for x in receipts),local_uniform_gain_total=sum(x['independent_uniform_local_classical_gain'] or 0 for x in receipts),all_local_means_evaluated=all(x['independent_uniform_local_classical_gain'] is not None for x in receipts),scope='Pure decoder and local classical guard algebra, arbitrary entry bits/internal MR. Local uniform numbers are NOT means over actual ABI inputs or gate counts. Donor zero, product equivalence and any rendered full circuit still require the independent universal checker. No candidate, simulator, failure census or nonce.',rows=receipts),indent=2)+'\n');print(out)
