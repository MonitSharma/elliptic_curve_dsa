"""Audit the reviewed frozen candidate and upload it once with user attribution."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = Path('/home/hclau/ecdsa_research')
OUT = ROOT / 'submission-wide95-703-20261018'
RUN = ROOT / 'wide95-703-20261018'
TREE = RUN / 'candidate'
REBUILD = ROOT / 'wide95-703-review-20261018-085419'
API = 'https://api.ecdsa.fail/api'
BENCH = '1ffb695a-309b-46b6-a728-2f97d8c7be74'

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2) + '\n')

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def git(*args):
    return subprocess.check_output(['git', '-C', str(TREE), *args])

def fetch(url):
    with urllib.request.urlopen(url, timeout=45) as r:
        return json.load(r)

review = json.loads((OUT / 'REVIEW.json').read_text())['wide95_plus703']
receipt = json.loads((RUN / 'BENCHMARK_RESULT.json').read_text())
assert receipt['status'] == 'UNCHANGED_BENCHMARK_PASS'
assert (receipt['qubits'], receipt['rounded_mean_toffoli'], receipt['product']) == (1863, 752991, 1402822233)
patch = git('diff', '--binary', 'HEAD', '--', 'src/point_add')
assert hashlib.sha256(patch).hexdigest() == review['patch_sha256'] == receipt['patch_sha256']
assert git('rev-parse', 'HEAD').decode().strip() == review['original_base_commit']
changed = git('diff', '--name-only', 'HEAD').decode().splitlines()
assert sorted(changed) == sorted(review['source_audit']['changed_files'])
assert not git('ls-files', '--others', '--exclude-standard', '--', 'src/point_add').strip()
for path, digest in json.loads((RUN / 'protected.json').read_text()).items():
    assert sha(TREE / path) == digest, path
for path in git('ls-files').decode().splitlines():
    if not path.startswith('src/point_add/'):
        assert (TREE / path).read_bytes() == git('show', 'HEAD:' + path), path
manifest = json.loads((REBUILD / 'source-manifest.json').read_text())
for path, digest in manifest.items():
    assert sha(TREE / path) == digest, path
assert sha(TREE / 'ops.bin') == review['final_stream_sha256'] == receipt['final_stream_sha256']
assert sha(REBUILD / 'benchmark.log') == review['fresh_reproduction']['benchmark_log_sha256']
assert (REBUILD / 'benchmark.exit').read_text().strip() == '0'
gate = json.loads((RUN / 'GATE.json').read_text())
assert gate['label'] == 'wide95-703-gate-20261018-v1' and gate['batches'] == 32768
assert all(v['status'] == 'FAILURE_GATE_PASS' and all(v['rules'].values()) for v in gate['verdicts'].values())
selection = json.loads((RUN / 'evidence/selection.json').read_text())
assert selection['nonce'] == 167 and selection['screened'] == 256 and selection['all_lower_nonces_fail']
note = OUT / 'SUBMISSION-NOTE.md'
assert 5120 <= note.stat().st_size <= 102400
snapshot = fetch(f'{API}/benchmarks/{BENCH}/submissions')
save('public-submissions-before.json', snapshot)
rows = [r for r in snapshot['submissions'] if
        (r['status'] == 'accepted' or (r['status'] == 'rejected' and r.get('rejectionReason') == 'score did not improve current best'))
        and r.get('officialMetrics') and r.get('officialScore') == r['officialMetrics']['qubits'] * r['officialMetrics']['toffoli']]
best = min(rows, key=lambda r: r['officialMetrics']['toffoli'])
assert best['id'] == 'b99c9678-5a68-49e8-a8b7-91fc6c383e37', 'Public parent changed; check gate eligibility'
assert receipt['rounded_mean_toffoli'] < best['officialMetrics']['toffoli']
assert not [r for r in snapshot['submissions'] if r.get('solverUsername') == 'MonitSharma' and r['status'] in ('queued', 'validating', 'running')]
audit = {'checked_at':datetime.now(timezone.utc).isoformat(), 'patch_sha256':receipt['patch_sha256'],
         'final_stream_sha256':receipt['final_stream_sha256'], 'source_manifest_entries_checked':len(manifest),
         'all_protected_tracked_files_match_base':True, 'changed_paths':changed,
         'benchmark_reproduction_log_sha256':sha(REBUILD / 'benchmark.log'), 'public_record':best,
         'model':'Gemini 4 Argon', 'harness':'Antigravity', 'note_sha256':sha(note),
         'gate_label':gate['label'], 'nonce':selection['nonce'], 'screened':selection['screened']}
save('PREUPLOAD-AUDIT.json', audit)
print(json.dumps({k:v for k,v in audit.items() if k != 'public_record'}, indent=2), flush=True)
if '--submit' not in sys.argv:
    raise SystemExit(0)
with (OUT / 'UPLOAD-STARTED.json').open('x') as f:
    json.dump({'started_at':datetime.now(timezone.utc).isoformat(), 'model':'Gemini 4 Argon', 'harness':'Antigravity'}, f)
with (OUT / 'submission-response.json').open('xb') as output, (OUT / 'submission-submit.err').open('xb') as error:
    result = subprocess.run(['/home/hclau/.local/bin/ecdsafail', 'submit', '--note-file', str(note),
        '--dependencies-file', str(OUT / 'DEPENDENCIES.json'), '--model', 'Gemini 4 Argon',
        '--harness', 'Antigravity', '--claimed-score', '1402822233', '--json'], cwd=TREE, stdout=output, stderr=error)
(OUT / 'upload.exit').write_text(str(result.returncode) + '\n')
if result.returncode:
    print((OUT / 'submission-submit.err').read_text(), flush=True)
    raise SystemExit(result.returncode)
response = json.loads((OUT / 'submission-response.json').read_text())
sid = response['submission']['id']
save('submission-status.json', fetch(f'{API}/submissions/{sid}'))
print(json.dumps({'id':sid, 'status':response['submission']['status']}), flush=True)
