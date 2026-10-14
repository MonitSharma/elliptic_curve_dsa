"""External terminal collection only; never launches or modifies a benchmark."""
from pathlib import Path
import hashlib,json,shutil,sys,time,datetime,subprocess
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');e=r/'evidence';prefix='ht25-bankswap-v2'
marker=e/f'{prefix}-official-eval-native.exit';wrapper=e/f'{prefix}-official-eval.exit'
if '--wait'in sys.argv:
 deadline=time.monotonic()+24*60*60
 while not(marker.exists()and wrapper.exists()):
  assert time.monotonic()<deadline,'24-hour collector timeout; no result claim'
  time.sleep(30)
assert marker.exists()and wrapper.exists(),'benchmark has no complete terminal markers; no result claim'
status=int(marker.read_text());log=e/f'{prefix}-official-eval.log';att=e/f'{prefix}-launch-attestation.json'
assert att.exists()and log.exists()
binding=json.loads(att.read_text());assert not binding['placeholder_used']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while c:=f.read(4*1024**2):h.update(c)
 return h.hexdigest()
assert sha(Path(binding['resolved_stream']))==binding['stream_sha256']
assert sha(r/'harness-ht25-v9/target/release/eval_circuit')==binding['protected_binary_sha256']
c=json.loads((e/f'candidate-{prefix}-manifest.json').read_text());source=Path(c['checkout'])
for p,h in c['source_sha256'].items():assert sha(source/p)==h,p
assert hashlib.sha256(subprocess.check_output(['git','-C',str(source),'diff','HEAD','--','src/point_add/'])).hexdigest()==c['patch_sha256']==binding['patch_sha256']
files={}
for name in ['score.json','results.tsv']:
 p=r/'harness-ht25-v9'/name
 if p.exists():
  target=e/f'{prefix}-official-{name}'
  if not target.exists():shutil.copy2(p,target)
  assert target.read_bytes()==p.read_bytes();files[name]=hashlib.sha256(target.read_bytes()).hexdigest()
receipt=dict(status='COMPLETE_NATIVE_PASS_PENDING_REVIEW'if status==0 else'COMPLETE_FAILED',collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),native_exit=status,wrapper_exit=int(wrapper.read_text()),qualified_score=False,scope='One unchanged protected benchmark on exact frozen full stream; coordinator reviews all9024 failure channels and complete terminal artifacts',stream_sha256=binding['stream_sha256'],patch_sha256=binding['patch_sha256'],N=binding['N'],protected_binary_sha256=binding['protected_binary_sha256'],log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),launch_attestation_sha256=hashlib.sha256(att.read_bytes()).hexdigest(),artifact_sha256=files)
(e/f'{prefix}-official-terminal-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
