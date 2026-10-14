"""Read-only research collection; no grader and no candidate edits."""
from pathlib import Path
import hashlib,json,re,tarfile,datetime,subprocess
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');e=r/'evidence'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while c:=f.read(4*1024**2):h.update(c)
 return h.hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
n=(e/'ht25-bankswap-v2-components.log').read_text();assert(e/'ht25-bankswap-v2-components.exit').read_text().strip()=='0'
groups=list(map(int,re.findall(r'test result: ok\. (\d+) passed; 0 failed',n)));assert groups==[7,5,2,1,2]
p=e/'ht25-bankswap-v2-decision';proof=(p/'native-proof.log').read_text();assert(p/'run.exit').read_text().strip()=='0'
assert 'test result: ok. 17 passed; 0 failed'in proof
instances=proof.count('DECISION_DIAGRAM_PHASE_PROOF');assert instances>0
binding=json.loads((p/'crate/complete-source-binding.json').read_text());assert len(binding['selected_native_tests'])==17
receipt=dict(status='COMPLETE_COMPONENT_ONLY',collected_utc=now,source='candidate-ht25-bankswap-v2',patch_sha256=binding['point_add_patch_sha256'],native_exit=0,native_groups=groups,proof_wrapper_exit=0,proof_selected_tests=17,ALLMR_instances=instances,kernel_sha256=binding['frozen_kernel_sha256'],native_log_sha256=sha(e/'ht25-bankswap-v2-components.log'),proof_log_sha256=sha(p/'native-proof.log'),proof_binding_sha256=sha(p/'crate/complete-source-binding.json'),scope='Fixed native lane values; all independent measurement outcomes. No full circuit generation/benchmark or all-curve claim.',failed_v1=dict(wrapper_exit=101,status='COMPILE_FAILED_NO_SIMULATION',log_sha256=sha(e/'ht25-bankswap-v1-components.log')))
(e/'ht25-bankswap-v2-component-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
meta=e/'ht25-v9-stream-metadata.json';exitfile=e/'ht25-v9-full-build.exit'
g=dict(status='RUNNING',collected_utc=now,wrapper_pid=2785256,native_pid=2785435,source='candidate-ht25-v9',patch_sha256='2d1c9652a8083d1fb1d7c2b7214c6051fb79fde003073426dda9367998b316c0',generation_log='evidence/ht25-v9-full-build.log',official_evaluation_launched=False,qualified_score=False)
if exitfile.exists():
 log=(e/'ht25-v9-full-build.log').read_text();stream=e/'ht25-v9-ops.bin'
 with stream.open('rb')as f:header=f.read(16)
 assert header[:8]==b'QECCOPSZ';N=int.from_bytes(header[8:],'little')
 assert 'EXACT_STREAM_SERIALIZER_PASS physical_ops=462 all_fields=true trusted_write_ops=true'in(e/'ht25-v9-serializer.log').read_text()
 assert 'Exit status: 0'in log
 digest=sha(stream);assert digest in log
 g.update(status='COMPLETE_GENERATION_BUT_MAX_OPS_BLOCKED'if N>4000000000 else'COMPLETE_DIAGNOSTIC',N=N,stream_sha256=digest,compressed_bytes=stream.stat().st_size,within_MAX_OPS=N<=4000000000,MAX_OPS=4000000000,wrapper_exit=int(exitfile.read_text().strip()),native_generation_time_exit=0,log_sha256=sha(e/'ht25-v9-full-build.log'),builder_binary_sha256=sha(r/'candidate-ht25-v9/target/release/build_circuit'))
 if N<=4000000000:
  m=json.loads(meta.read_text());assert m['sizeof_op']==56 and m['ops']==N and m['referenced_qubits']<=692 and log.count('Exit status: 0')>=2
  g.update(referenced_qubits=m['referenced_qubits'],sizeof_op=56,op_vec_bytes=m['op_vec_bytes'],native_metadata_time_exit=0,metadata_sha256=sha(meta),wrapper_bookkeeping_failed=g['wrapper_exit']!=0)
(e/'ht25-v9-generation-receipt.json').write_text(json.dumps(g,indent=2)+'\n')
logs=[]
for path in e.rglob('*'):
 if path.is_file()and path.suffix in ('.log','.exit','.pid')and 'ht25'in path.as_posix():
  if path.name.endswith('-full-build.log')and not(e/path.name.replace('.log','.exit')).exists():continue
  logs.append(path)
archive=e/'ht25-final-completed-logs-v2.tar.gz'
with tarfile.open(archive,'w:gz')as t:
 for path in sorted(logs):t.add(path,arcname=path.relative_to(e).as_posix())
(e/'ht25-final-log-index-v2.json').write_text(json.dumps(dict(collected_utc=now,archive_sha256=sha(archive),files=[dict(path=x.relative_to(e).as_posix(),sha256=sha(x))for x in sorted(logs)]),indent=2)+'\n')
print(json.dumps(dict(bank=receipt,generation=g,archive_sha256=sha(archive)),indent=2))
