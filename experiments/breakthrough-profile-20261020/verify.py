"""Reject all diagnostic measurements unless the complete output is unchanged."""
import hashlib
import json
import subprocess
from pathlib import Path

r = Path(__file__).resolve().parent
t = r / 'observer'
freeze = json.loads((r / 'SOURCE_FREEZE.json').read_text())
def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()
assert all(sha(t / name) == digest for name, digest in {**freeze['source_files'], **freeze['protected_files']}.items())
actual = sha(t / 'ops.bin')
assert actual == freeze['expected_final_stream_sha256'], 'Instrumentation changed emitted circuit; profile inadmissible'
phases = []
for line in (r / 'generate.log').read_text().splitlines():
    if line.startswith('BREAK_PHASE\t'):
        name, end, active, peak, ccx, ccz = line.split('\t')[1:]
        phases.append({'phase': name, 'prepass_end': int(end), 'active_at_end': int(active),
                       'builder_phase_peak': int(peak), 'emitted_ccx': int(ccx), 'emitted_ccz': int(ccz)})
assert phases and all(a['prepass_end'] <= b['prepass_end'] for a,b in zip(phases,phases[1:]))
assert {'divide', 'square', 'multiply'}.issubset({p['phase'] for p in phases})
result = {'status':'BYTE_IDENTICAL_ACCEPTED_CIRCUIT_DIAGNOSTIC_PROFILE', 'stream_sha256':actual,
          'prepass_stream_sha256':sha(t / 'prepass.ops.bin'), 'phases':phases,
          'protected_files_unchanged':True, 'not_a_new_score_or_gate':True}
(r / 'PHASE-PROFILE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
