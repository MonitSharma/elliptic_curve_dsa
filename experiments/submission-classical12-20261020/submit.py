"""Verify the frozen source and submit once; never retry an uncertain upload."""
import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
FINAL = OUT.parent / 'classical12-final-20261020'
TREE = FINAL / 'candidate'
API = 'https://api.ecdsa.fail/api'
BENCH = '1ffb695a-309b-46b6-a728-2f97d8c7be74'
PARENT = '9dc3798c-93e0-4da4-a6a9-37586737c4af'

def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

def git(*args):
    return subprocess.check_output(['git', '-C', str(TREE), *args])

def fetch(path):
    with urllib.request.urlopen(API + path, timeout=60) as r:
        return json.load(r)

assert not (OUT / 'UPLOAD-STARTED.json').exists(), 'Inspect existing receipt/status; do not duplicate upload'
freeze = json.loads((FINAL / 'SOURCE_FREEZE.json').read_text())
assert git('rev-parse', 'HEAD').decode().strip() == freeze['base_revision']
for path, digest in freeze['source_files'].items():
    assert sha(TREE / path) == digest, path
assert {p.relative_to(TREE).as_posix() for p in (TREE / 'src/point_add').rglob('*') if p.is_file()} == set(freeze['source_files'])
protected = []
for path in git('ls-files').decode().splitlines():
    if not path.startswith('src/point_add/'):
        assert (TREE / path).read_bytes() == git('show', 'HEAD:' + path), path
        protected.append(path)
assert len(protected) == 17 and len(freeze['source_files']) == 180
patch = git('diff', '--binary', 'HEAD', '--', 'src/point_add')
assert hashlib.sha256(patch).hexdigest() == freeze['patch_sha256']
assert sha(TREE / 'ops.bin') == '125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501'
assert sha(FINAL / 'benchmark.log') == 'd79959df90f6443ce24ca7529ef32b1beece46b18f6d684b0ef9428b219df8a4'
assert sha(FINAL / 'score.json') == '66f7d720c59b8e9e3c452dd636540d7239d6a54c092717c4570bf697a324c0ff'
assert sha(FINAL / 'final-evidence.tar.gz') == 'eaea21485b71865b4fcd2e2011cafe0ededc9341a5c06ad88427b7c8f14bfb9d'
assert 'all 9024 shots OK' in (FINAL / 'benchmark.log').read_text()
assert '=== experiment OK ===' in (FINAL / 'benchmark.log').read_text()
score = json.loads((FINAL / 'score.json').read_text())
assert score == {'score': 939169018, 'metrics': {'toffoli': 761077, 'qubits': 1234}}
audit = json.loads((FINAL / 'INDEPENDENT-FINAL-AUDIT.json').read_text())
assert audit['gate_rules_pass'] and audit['lowest_pass_complete_audit'] and audit['benchmark_failures'] == 0
note = OUT / 'SUBMISSION-NOTE-OFFICIAL.md'
assert 5120 <= note.stat().st_size <= 102400
snapshot = fetch('/benchmarks/' + BENCH + '/submissions')
save('public-submissions-before.json', snapshot)
save('public-benchmark-before.json', fetch('/benchmarks/' + BENCH))
eligible = [r for r in snapshot['submissions'] if
            (r['status'] == 'accepted' or (r['status'] == 'rejected' and r.get('rejectionReason') == 'score did not improve current best'))
            and r.get('officialMetrics') and r.get('officialScore') == r['officialMetrics']['qubits'] * r['officialMetrics']['toffoli']]
parent = min(eligible, key=lambda r: r['officialScore'])
assert parent['id'] == PARENT, 'Public parent changed; assess existing qualification before upload'
assert parent['officialScore'] == 939192464 and score['score'] < parent['officialScore']
pending = [r['id'] for r in snapshot['submissions'] if r.get('solverUsername') == 'MonitSharma' and r['status'] in ('queued', 'validating', 'running')]
assert not pending, pending
save('PREUPLOAD-AUDIT.json', {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
     'base_revision': freeze['base_revision'], 'source_files_checked': 180, 'protected_files_checked': len(protected),
     'patch_sha256': freeze['patch_sha256'], 'stream_sha256': sha(TREE / 'ops.bin'),
     'note_sha256': sha(note), 'dependencies_sha256': sha(OUT / 'DEPENDENCIES.json'),
     'model': 'GPT-6 sol', 'harness': 'Codex', 'model_attribution_authorized_by_user': True,
     'parent_id': parent['id'], 'parent_product': parent['officialScore'],
     'candidate_product': score['score'], 'improvement': parent['officialScore'] - score['score'],
     'gate_and_complete_nonce_audit_preserved': True})
print('Pre-upload verification PASS: Q1234 T761077 product939169018; public parent unchanged.', flush=True)
if '--submit' not in sys.argv:
    raise SystemExit(0)
with (OUT / 'UPLOAD-STARTED.json').open('x') as f:
    json.dump({'started_at_utc': datetime.now(timezone.utc).isoformat(), 'model': 'GPT-6 sol', 'harness': 'Codex'}, f)
with (OUT / 'submission-response.json').open('xb') as output, (OUT / 'submission-submit.err').open('xb') as error:
    result = subprocess.run(['/home/hclau/.local/bin/ecdsafail', 'submit', '--note-file', str(note),
        '--dependencies-file', str(OUT / 'DEPENDENCIES.json'), '--model', 'GPT-6 sol',
        '--harness', 'Codex', '--claimed-score', '939169018', '--json'],
        cwd=TREE, stdout=output, stderr=error)
(OUT / 'upload.exit').write_text(str(result.returncode) + '\n')
assert result.returncode == 0, 'Inspect submission response and stderr; never blindly retry'
response = json.loads((OUT / 'submission-response.json').read_text())
sid = response['submission']['id']
save('submission-status.json', fetch('/submissions/' + sid))
print(json.dumps({'id': sid, 'status': response['submission']['status']}), flush=True)
