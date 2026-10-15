"""Strict last-write zero audit for every source-defined N2 return destination."""
import hashlib,json,struct,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'loan-normal-forms-20261016';other=r.parent/'current-value-attribution-20261016'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
markers=json.loads((other/'actual-loan-markers.json').read_text());stream=r/'tip/ops.bin';assert sha(stream)==markers['actual_stream_sha256']
families={}
for m in markers['markers']:
 if m['label']=='in-before':families.setdefault(m['phase'],{})['before']=m['at']
 if m['label']=='in-after':families.setdefault(m['phase'],{})['destinations']=m['rail0'][:4]+m['rail1'][:4]
queries={v['before']:(k,v['destinations'])for k,v in families.items()};end=max(queries)
last={};inputs=set();depth=0;rows=[];index=0;S=(1<<64)-1
with stream.open('rb',buffering=0)as source:
 magic,n=struct.unpack('<8sQ',source.read(16));assert magic==b'QECCOPSZ';proc=subprocess.Popen(['zstd','-dcq'],stdin=source,stdout=subprocess.PIPE)
 while index<=end:
  count=min(65536,end+1-index);raw=proc.stdout.read(count*56);assert len(raw)==count*56
  for op in struct.iter_unpack('<7Q',raw):
   if index in queries:
    phase,targets=queries[index];results=[]
    for q in targets:
     w=last.get(q);proved=(w is None and q not in inputs)or(w is not None and w['kind']in(11,12)and w['depth']==0 and w['condition']==S)
     results.append(dict(q=q,proved_zero=proved,last_value_write=w,initial_quantum_ABI=q in inputs))
    rows.append(dict(phase=phase,at=index,results=results))
   k,b,a,t,ct,cc,reg=op
   if k==2 and t!=S:inputs.add(t)
   targets=[t]if k in(6,8,11,12,13)else([a,t]if k==10 else [])
   for q in targets:last[q]=dict(at=index,kind=k,depth=depth,condition=cc)
   if k==15:depth+=1
   if k==16:depth-=1;assert depth>=0
   index+=1
 # Drain, so no decompressor SIGPIPE or guessed partial-stream success.
 while proc.stdout.read(8*1024*1024):pass
 assert proc.wait()==0
assert len(rows)==2 and sum(len(x['results'])for x in rows)==16 and sha(stream)==markers['actual_stream_sha256']
out=d/'STRUCTURAL_RETURN_ZERO_AUDIT.json';assert not out.exists()
out.write_text(json.dumps(dict(status='STRICT_SOURCE_LAST_WRITE_ZERO_AUDIT',stream_sha256=sha(stream),marker_sha256=sha(other/'actual-loan-markers.json'),audit_source_sha256=sha(Path(__file__)),proved=sum(y['proved_zero']for x in rows for y in x['results']),total=16,rows=rows,scope='Counts both Swap endpoints and every possible conditional value write. Only a last depth-zero unconditionally executed R/HMR or never-written non-input scratch proves zero. Does not prove phase, a repair, or identities on other inputs.'),indent=2)+'\n');print(out)
