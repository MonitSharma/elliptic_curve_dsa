"""External fail-closed guards; protected evaluator remains unchanged."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits')
mode=sys.argv[1];assert mode in ('reserve','evaluate','launch')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while chunk:=f.read(4*1024**2):h.update(chunk)
 return h.hexdigest()
assert (r/'evidence/headflag-v1-official-eval-native.exit').exists()
for name in ['ht25-bankswap-v2-full-build.exit','ht25-v9-harness-build-v2.exit']:
 assert (r/'evidence'/name).read_text().strip()=='0',name
g=json.loads((r/'evidence/ht25-bankswap-v2-generation-receipt.json').read_text())
assert g['status']=='COMPLETE_DIAGNOSTIC' and g['within_MAX_OPS']
assert (r/'evidence/ht25-bankswap-v2-components.exit').read_text().strip()=='0'
assert (r/'evidence/ht25-bankswap-v2-decision/run.exit').read_text().strip()=='0'
import re
assert list(map(int,re.findall(r'test result: ok\. (\d+) passed; 0 failed',(r/'evidence/ht25-bankswap-v2-components.log').read_text())))==[7,5,2,1,2]
proof=(r/'evidence/ht25-bankswap-v2-decision/native-proof.log').read_text();assert 'test result: ok. 17 passed; 0 failed'in proof and proof.count('DECISION_DIAGRAM_PHASE_PROOF')==704
assert 'EXACT_STREAM_SERIALIZER_PASS physical_ops=462 all_fields=true trusted_write_ops=true'in(r/'evidence/ht25-bankswap-v2-serializer.log').read_text()
N=g['N'];assert N<=4000000000
m=json.loads((r/'evidence/ht25-bankswap-v2-stream-metadata.json').read_text())
assert m['ops']==N and m['referenced_qubits']<=692 and m['sizeof_op']==56 and m['op_vec_bytes']==N*56
stream=r/'evidence/ht25-bankswap-v2-ops.bin';assert digest(stream)==g['stream_sha256']
with stream.open('rb')as f:header=f.read(16)
assert header[:8]==b'QECCOPSZ'and int.from_bytes(header[8:],'little')==N
ps=subprocess.check_output(['ps','-eo','pid=,rss=,comm=,args='],text=True);large=[]
for line in ps.splitlines():
 w=line.strip().split(None,3)
 if len(w)==4 and(w[2]=='eval_circuit'or('/home/hclau/ecdsa_research'in w[3]and int(w[1])>16*1024**2)):large.append(w)
assert not large,large
pre=json.loads(subprocess.check_output(['python3','/home/hclau/ecdsa_research/server-preflight.py'],text=True))
limit=268435456*1024;need=N*56+16*2**30
assert need<limit and need<pre['memory']['MemAvailable_bytes'],(need,limit,pre['memory'])
c=json.loads((r/'evidence/candidate-ht25-bankswap-v2-manifest.json').read_text());s=Path(c['checkout'])
assert c['patch_sha256']=='61bd0d94831feea58dee9fc1c6a9cc2db10ed32e9a65f95ed5ebfe33a9a32f43'
assert digest(r/'evidence/candidate-ht25-bankswap-v2.patch')==c['patch_sha256']
assert hashlib.sha256(subprocess.check_output(['git','-C',str(s),'diff','HEAD','--','src/point_add/'])).hexdigest()==c['patch_sha256']
assert subprocess.check_output(['git','-C',str(s),'rev-parse','HEAD'],text=True).strip()==c['base_revision']
changed=subprocess.check_output(['git','-C',str(s),'diff','HEAD','--name-only'],text=True).splitlines()
assert sorted(changed)==sorted(c['candidate_changed_paths'])and all(p.startswith('src/point_add/')for p in changed)
for p,h in c['source_sha256'].items():assert digest(s/p)==h,p
t=json.loads((r/'evidence/ht25-v9-protected-harness-manifest.json').read_text());harness=Path(t['checkout'])
assert harness==r/'harness-ht25-v9'
assert subprocess.check_output(['git','-C',str(harness),'rev-parse','HEAD'],text=True).strip()==t['base_revision']==c['base_revision']
protected={}
for p in subprocess.check_output(['git','-C',str(harness),'ls-files'],text=True).splitlines():
 if p in ('results.tsv','score.json'):continue
 actual=(harness/p).read_bytes();original=subprocess.check_output(['git','-C',str(harness),'show','HEAD:'+p]);assert actual==original,p
 protected[p]=hashlib.sha256(actual).hexdigest()
assert digest(harness/'target/release/eval_circuit')==t['protected_binary_sha256']
assert not(harness/'results.tsv').exists()and not(harness/'score.json').exists()
assert not subprocess.check_output(['git','-C',str(harness),'status','--porcelain'],text=True).strip()
assert digest(r/'stream-resource-meta/target/release/qubit_stream_resource_meta')=='e0a15f3bf58d0e7731321fded824962cf3a4ff6c07dc4556553960ce6efe042e'
if mode=='launch':assert(harness/'ops.bin').is_symlink()and(harness/'ops.bin').resolve()==stream.resolve()
else:assert not os.path.lexists(harness/'ops.bin')
if mode in ('evaluate','launch'):
 reserved=json.loads((r/'evidence/ht25-bankswap-v2-stream-reserved-metadata.json').read_text());assert reserved['measured_loader_vec_capacity']==N and reserved['sizeof_op']==56 and reserved['ops']==N
 if mode=='evaluate':(harness/'ops.bin').symlink_to(stream)
receipt=dict(scope='External resource/source guards only; unchanged protected harness; no score',mode=mode,N=N,stream_sha256=g['stream_sha256'],patch_sha256=c['patch_sha256'],sizeof_op=56,op_vec_bytes=N*56,need_plus_margin_bytes=need,virtual_cap_bytes=limit,available_bytes=pre['memory']['MemAvailable_bytes'],other_large_ECDSA_processes=large,protected_binary_sha256=t['protected_binary_sha256'],protected_source_sha256=protected,input_path=str(harness/'ops.bin'),resolved_stream=str(stream),placeholder_used=False)
(r/f'evidence/ht25-bankswap-v2-{mode}-attestation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,sort_keys=True))
