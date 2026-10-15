"""Read-only qualification review of the already-completed 692-qubit evaluation.

No generation, evaluator, packet selection, or submission is invoked. Writes
only a new review receipt in the follow-up evidence directory.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');e=r/'evidence'
prefix='ht25-bankswap-v2'
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
terminal=json.loads((e/f'{prefix}-official-terminal-receipt.json').read_text())
binding=json.loads((e/f'{prefix}-launch-attestation.json').read_text())
manifest=json.loads((e/f'candidate-{prefix}-manifest.json').read_text())
generation=json.loads((e/f'{prefix}-generation-receipt.json').read_text())
source=Path(manifest['checkout']);harness=r/'harness-ht25-v9'
assert terminal['native_exit']==terminal['wrapper_exit']==0
for f in ['official-eval-native.exit','official-eval.exit','official-cycle.exit']:
    assert (e/f'{prefix}-{f}').read_text().strip()=='0'
assert not binding['placeholder_used']
assert digest(Path(binding['resolved_stream']))==binding['stream_sha256']==terminal['stream_sha256']==generation['stream_sha256']
assert digest(harness/'target/release/eval_circuit')==binding['protected_binary_sha256']==terminal['protected_binary_sha256']
assert digest(e/f'{prefix}-launch-attestation.json')==terminal['launch_attestation_sha256']
assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==manifest['base_revision']
patch=subprocess.check_output(['git','-C',str(source),'diff','HEAD','--','src/point_add/'])
assert hashlib.sha256(patch).hexdigest()==manifest['patch_sha256']==terminal['patch_sha256']
changed=subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines()
assert sorted(changed)==sorted(manifest['candidate_changed_paths'])
assert all(p.startswith('src/point_add/') for p in changed)
for p,h in manifest['source_sha256'].items():assert digest(source/p)==h,p
for p,h in binding['protected_source_sha256'].items():assert digest(harness/p)==h,p
log=e/f'{prefix}-official-eval.log';text=log.read_text()
assert digest(log)==terminal['log_sha256']
assert re.search(r'tested shots\s*:\s*9024',text) and 'all 9024 shots OK' in text
for name in ['classical mismatches','phase-garbage batches','ancilla-garbage batches']:
    assert re.search(re.escape(name)+r'\s*:\s*0\b',text),name
score_path=e/f'{prefix}-official-score.json';score=json.loads(score_path.read_text())
assert digest(score_path)==terminal['artifact_sha256']['score.json']
assert digest(e/f'{prefix}-official-results.tsv')==terminal['artifact_sha256']['results.tsv']
assert score_path.read_bytes()==(harness/'score.json').read_bytes()
assert (e/f'{prefix}-official-results.tsv').read_bytes()==(harness/'results.tsv').read_bytes()
assert score['metrics']==dict(toffoli=1481382858,qubits=692)
assert score['score']==score['metrics']['toffoli']*score['metrics']['qubits']
total=int(re.search(r'total Toffoli \(sum\)\s*:\s*(\d+) over 9024 shots',text)[1])
assert (total+4512)//9024==score['metrics']['toffoli']
native=(e/f'{prefix}-components.log').read_text();phase=(e/f'{prefix}-decision/native-proof.log').read_text()
assert list(map(int,re.findall(r'test result: ok\. (\d+) passed; 0 failed',native)))==[7,5,2,1,2]
assert 'test result: ok. 17 passed; 0 failed' in phase and phase.count('DECISION_DIAGRAM_PHASE_PROOF')==704
assert 'EXACT_STREAM_SERIALIZER_PASS physical_ops=462 all_fields=true trusted_write_ops=true' in (e/f'{prefix}-serializer.log').read_text()
receipt=dict(status='complete_local_benchmark_pass_reviewed',reviewed_at_utc=datetime.now(timezone.utc).isoformat(),
    provenance='Overnight candidate completed during this follow-up; newly collected result, not newly invented source',
    baseline_revision=manifest['base_revision'],candidate_source=str(source),candidate_changed_paths=changed,
    source_sha256=manifest['source_sha256'],patch_sha256=terminal['patch_sha256'],
    stream_sha256=terminal['stream_sha256'],protected_binary_sha256=terminal['protected_binary_sha256'],
    log_sha256=terminal['log_sha256'],terminal_receipt_sha256=digest(e/f'{prefix}-official-terminal-receipt.json'),
    launch_attestation_sha256=terminal['launch_attestation_sha256'],source_and_protected_files_rechecked=True,
    protected_evaluator_unchanged=True,exact_generated_stream_used=True,placeholder_used=False,
    shots=9024,classical_mismatches=0,phase_garbage_batches=0,ancilla_garbage_batches=0,
    native_exit=0,wrapper_exit=0,score=score,total_executed_toffoli=total,
    native_component_tests=17,exact_phase_tests=17,fixed_input_all_measurement_instances=704,
    serializer_fixture_operations=462,benchmark_qualified=True,officially_submitted=False,
    all_input_correctness_proved=False,submission_packaging_qualified=False,
    limitation='Finite benchmark pass; quotient/precision boundary limitations remain. External streamed generation and unchanged protected evaluator are bound; standard submission packaging is not yet qualified.',
    previous_public_width=693,width_reduction=1,improved_objective='qubits_only',
    evidence_directory=str(e))
out=Path('/home/hclau/ecdsa_research/followup-20261015/bankswap-reviewed-receipt.json')
out.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['status','shots','score','width_reduction','improved_objective','all_input_correctness_proved','submission_packaging_qualified']},indent=2))
