"""Independent read-only verification of terminal evidence; never runs scorer."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import hashlib,json,re,subprocess

root=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits')
e=root/'evidence';prefix='ht25-bankswap-v2'
base='c95b9325913abacca9c86bdebad10a20633cd04e'
patch_sha='61bd0d94831feea58dee9fc1c6a9cc2db10ed32e9a65f95ed5ebfe33a9a32f43'
stream_sha='03cb7a3f0cc5bbb1c4d07a3cfed809e3623137425ebd7c725f158737f4a77739'
binary_sha='88b6fd33dfcd85b317ed6694c10715dbb6b4d5926838400ec7c4e23cdda77e3a'
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(p,*args):return subprocess.check_output(['git','-C',str(p),*args])
candidate=root/'candidate-ht25-bankswap-v2';harness=root/'harness-ht25-v9'
manifest=json.loads((e/f'candidate-{prefix}-manifest.json').read_text(encoding='utf8'))
assert git(candidate,'rev-parse','HEAD').decode().strip()==base
actual_patch=git(candidate,'diff','HEAD','--','src/point_add/')
assert hashlib.sha256(actual_patch).hexdigest()==patch_sha==manifest['patch_sha256']
changed=git(candidate,'diff','HEAD','--name-only').decode().splitlines()
assert sorted(changed)==sorted(manifest['candidate_changed_paths'])
assert all(p.startswith('src/point_add/')for p in changed)
assert not git(candidate,'ls-files','--others','--exclude-standard').strip()
for p,h in manifest['source_sha256'].items():assert sha(candidate/p)==h,p
candidate_protected=0
for p in git(candidate,'ls-files').decode().splitlines():
    if p.startswith('src/point_add/'):continue
    assert (candidate/p).read_bytes()==git(candidate,'show','HEAD:'+p),p
    candidate_protected+=1
assert git(harness,'rev-parse','HEAD').decode().strip()==base
harness_protected=0
for p in git(harness,'ls-files').decode().splitlines():
    if p in ('score.json','results.tsv'):continue
    assert (harness/p).read_bytes()==git(harness,'show','HEAD:'+p),p
    harness_protected+=1
assert sha(harness/'target/release/eval_circuit')==binary_sha
library=(harness/'src/lib.rs').read_text(encoding='utf8')
assert re.findall(r'^pub mod (\w+);',library,re.M)==['circuit','sim','weierstrass_elliptic_curve']
stream=e/f'{prefix}-ops.bin'
assert sha(stream)==stream_sha
assert (harness/'ops.bin').is_symlink()and(harness/'ops.bin').resolve()==stream
with stream.open('rb')as f:header=f.read(16)
assert header[:8]==b'QECCOPSZ';n=int.from_bytes(header[8:],'little')
assert n==2472354640
for suffix in ('official-eval-native.exit','official-eval.exit','official-cycle.exit'):
    assert(e/f'{prefix}-{suffix}').read_text(encoding='utf8').strip()=='0',suffix
log=e/f'{prefix}-official-eval.log';text=log.read_text(encoding='utf8')
assert 'all 9024 shots OK'in text and '=== experiment OK ==='in text
shots=int(re.search(r'tested shots\s*:\s*(\d+)',text)[1]);assert shots==9024
for k in ('classical mismatches','phase-garbage batches','ancilla-garbage batches'):
    assert int(re.search(re.escape(k)+r'\s*:\s*(\d+)',text)[1])==0,k
assert int(re.search(r'qubits\s*:\s*(\d+)',text)[1])==692
total=int(re.search(r'total Toffoli \(sum\)\s*:\s*(\d+) over 9024 shots',text)[1])
mean=Fraction(total,shots);rounded=(2*total+shots)//(2*shots)
score=json.loads((harness/'score.json').read_text(encoding='utf8'))
assert score['metrics']=={'qubits':692,'toffoli':rounded}
assert rounded==1481382858 and score['score']==692*rounded==1025116937736
for name in ('score.json','results.tsv'):
    assert(harness/name).read_bytes()==(e/f'{prefix}-official-{name}').read_bytes()
att=json.loads((e/f'{prefix}-launch-attestation.json').read_text(encoding='utf8'))
assert att['placeholder_used']is False and att['stream_sha256']==stream_sha and att['N']==n
assert att['protected_binary_sha256']==binary_sha
assert att['op_vec_bytes']==n*56
assert att['need_plus_margin_bytes']<min(att['available_bytes'],att['virtual_cap_bytes'])
for p,h in att['protected_source_sha256'].items():assert sha(harness/p)==h,p
receipt=dict(status='INDEPENDENTLY_VERIFIED_COMPLETE_LOCAL_Q692_PASS',
 verified_utc=datetime.now(timezone.utc).isoformat(),host=subprocess.check_output(['hostname'],text=True).strip(),
 base_revision=base,changed_paths=changed,candidate_protected_files_checked=candidate_protected,
 harness_tracked_source_files_checked=harness_protected,patch_sha256=patch_sha,stream_sha256=stream_sha,
 protected_binary_sha256=binary_sha,log_sha256=sha(log),score_sha256=sha(harness/'score.json'),
 tested_shots=shots,failures={'value':0,'phase_batches':0,'ancilla_batches':0},
 N=n,qubits=692,total_executed_toffoli=total,exact_mean=str(mean),rounded_mean_toffoli=rounded,
 product=score['score'],placeholder_scored=False,benchmark_rerun=False,
 normal_submission_generation_tested=False,all_input_correctness_proved=False)
print(json.dumps(receipt,indent=2))
