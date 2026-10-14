"""Read-only generation attestation; preserves native and wrapper status separately."""
from pathlib import Path
import hashlib,json,re,sys,datetime,subprocess
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');e=r/'evidence'
v=sys.argv[1];assert v in ('ht25-v9','ht25-bankswap-v2')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while c:=f.read(4*1024**2):h.update(c)
 return h.hexdigest()
c=json.loads((e/f'candidate-{v}-manifest.json').read_text());s=Path(c['checkout'])
assert sha(e/f'candidate-{v}.patch')==c['patch_sha256']
assert subprocess.check_output(['git','-C',str(s),'rev-parse','HEAD'],text=True).strip()==c['base_revision']
for p,h in c['source_sha256'].items():assert sha(s/p)==h,p
changed=subprocess.check_output(['git','-C',str(s),'diff','HEAD','--name-only'],text=True).splitlines();assert sorted(changed)==sorted(c['candidate_changed_paths'])and all(p.startswith('src/point_add/')for p in changed)
protected=json.loads((e/f'{v}-full-build-protected-source.json').read_text())
for p,h in protected.items():assert sha(s/p)==h,p
assert(e/f'{v}-components.exit').read_text().strip()=='0'
groups=[6,5,2,1,2]if v=='ht25-v9'else[7,5,2,1,2]
assert list(map(int,re.findall(r'test result: ok\. (\d+) passed; 0 failed',(e/f'{v}-components.log').read_text())))==groups
proof=e/('ht25-v9-decision-v3'if v=='ht25-v9'else'ht25-bankswap-v2-decision')
assert(proof/'run.exit').read_text().strip()=='0'
pl=(proof/'native-proof.log').read_text();count=16 if v=='ht25-v9'else 17;instances=576 if v=='ht25-v9'else 704
assert f'test result: ok. {count} passed; 0 failed'in pl and pl.count('DECISION_DIAGRAM_PHASE_PROOF')==instances
assert 'EXACT_STREAM_SERIALIZER_PASS physical_ops=462 all_fields=true trusted_write_ops=true'in(e/f'{v}-serializer.log').read_text()
receipt=dict(status='RUNNING',collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=str(s),patch_sha256=c['patch_sha256'],source_sha256=c['source_sha256'],source_attested=True,protected_source_sha256=protected,serializer_fixture_ops=462,native_tests=sum(groups),ALLMR_tests=count,ALLMR_instances=instances,wrapper_pid=int((e/f'{v}-full-build.pid').read_text()),builder_binary_sha256=sha(s/'target/release/build_circuit'),generation_log=f'evidence/{v}-full-build.log',official_evaluation_launched=False,qualified_score=False)
marker=e/f'{v}-full-build.exit';meta=e/f'{v}-stream-metadata.json'
if marker.exists():
 log=(e/f'{v}-full-build.log').read_text();stream=e/f'{v}-ops.bin'
 with stream.open('rb')as f:header=f.read(16)
 assert header[:8]==b'QECCOPSZ';N=int.from_bytes(header[8:],'little');digest=sha(stream);assert digest in log
 assert 'Exit status: 0'in log
 receipt.update(status='COMPLETE_DIAGNOSTIC'if N<=4000000000 else'COMPLETE_GENERATION_BUT_MAX_OPS_BLOCKED',N=N,MAX_OPS=4000000000,within_MAX_OPS=N<=4000000000,stream_sha256=digest,compressed_bytes=stream.stat().st_size,native_generation_time_exit=0,wrapper_exit=int(marker.read_text()),wrapper_bookkeeping_failed=int(marker.read_text())!=0,log_sha256=sha(e/f'{v}-full-build.log'))
 if N<=4000000000:
  m=json.loads(meta.read_text());assert m['ops']==N and m['sizeof_op']==56 and m['referenced_qubits']<=692 and log.count('Exit status: 0')>=2
  receipt.update(referenced_qubits=m['referenced_qubits'],sizeof_op=56,op_vec_bytes=m['op_vec_bytes'],native_metadata_time_exit=0,metadata_sha256=sha(meta))
(e/f'{v}-generation-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,sort_keys=True))
