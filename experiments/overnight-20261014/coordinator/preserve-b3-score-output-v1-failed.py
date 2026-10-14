"""Preserve scorer outputs at their compiled manifest path, then restore history."""
from pathlib import Path
import hashlib
import json
import subprocess

root=Path('/home/hclau/ecdsa_research/overnight-20261014')
source=root/'coordinator-b3-classical'
evidence=root/'coordinator-b3-reference-eval'
assert source.resolve()==root/'coordinator-b3-classical'
assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()=='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
assert (evidence/'run.exit').read_text().strip()=='0'
log=(evidence/'run.log').read_text()
assert 'all 9024 shots OK' in log and 'classical mismatches    : 0' in log
observed=(source/'results.tsv').read_bytes()
original=subprocess.check_output(['git','-C',str(source),'show','HEAD:results.tsv'])
assert observed.startswith(original),'Historical prefix must be byte-identical'
newrows=observed[len(original):]
assert b'B3 public Toffoli source' in newrows and b'Clean unchanged B3 public baseline reproduction' in newrows
score=(source/'score.json').read_bytes()
decoded=json.loads(score)
assert decoded=={'score':940027660,'metrics':{'toffoli':761156,'qubits':1235}}
(evidence/'run/score.json').write_bytes(score)
(evidence/'run/new-results.tsv').write_bytes(newrows)
(evidence/'observed-full-results.tsv').write_bytes(observed)
(source/'results.tsv').write_bytes(original)
oldscore=subprocess.check_output(['git','-C',str(source),'show','HEAD:score.json'])
(source/'score.json').write_bytes(oldscore)
out={'scope':'Unchanged protected evaluator writes score/results at CARGO_MANIFEST_DIR, not input cwd. Actual fresh output preserved; original historical bytes restored after copying our appended rows.',
     'compiled_manifest_dir':str(source),'baseline_revision':'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7',
     'original_historical_results_sha256':hashlib.sha256(original).hexdigest(),'observed_full_results_sha256':hashlib.sha256(observed).hexdigest(),
     'new_rows_sha256':hashlib.sha256(newrows).hexdigest(),'score_sha256':hashlib.sha256(score).hexdigest(),
     'score':decoded,'initial_collector_status':'incomplete_or_inadmissible_evidence because requested cwd score path absent',
     'repeat_evaluation':False,'historical_prefix_unchanged':True,'historical_score_restored_sha256':hashlib.sha256(oldscore).hexdigest()}
(evidence/'output-location-provenance.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
