from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parent;e=root/'evidence'
assert (e/'benchmark.exit').read_text().strip()=='0'
log=(e/'benchmark.log').read_text();score=json.loads((e/'score.json').read_text())
assert 'all 9024 shots OK' in log
patterns={'value':'classical mismatches','phase_batches':'phase-garbage batches','ancilla_batches':'ancilla-garbage batches'}
failures={k:int(re.search(re.escape(v)+r'\s*:\s*(\d+)',log)[1]) for k,v in patterns.items()}
assert not any(failures.values())
total=int(re.search(r'total Toffoli \(sum\)\s*:\s*(\d+) over 9024 shots',log)[1]);t=(total+4512)//9024
assert score['metrics']=={'toffoli':t,'qubits':1464} and score['score']==1464*t
selection=json.loads((e/'selection.json').read_text())
receipt={'status':'COMPLETE_UNCHANGED_BENCHMARK_PASS_FINAL_CENSUS_PENDING','source_revision':json.loads((e/'FREEZE.json').read_text())['base_revision'],'shots':9024,'failures':failures,'total_executed_toffoli':total,'rounded_mean_executed_toffoli':t,'mean_executed_toffoli':total/9024,'qubits':1464,'product':1464*t,'nonce':selection['nonce'],'nonces_screened':selection['screened'],'nonce_policy':selection['policy'],'submission_mode':'queue','submitted':False,'stream_sha256':(e/'final-stream.sha256').read_text().split()[0],'patch_sha256':hashlib.sha256((e/'final-candidate.patch').read_bytes()).hexdigest(),'benchmark_log_sha256':hashlib.sha256((e/'benchmark.log').read_bytes()).hexdigest(),'protected_file_manifest_sha256':hashlib.sha256((e/'protected.json').read_bytes()).hexdigest()}
(root/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
