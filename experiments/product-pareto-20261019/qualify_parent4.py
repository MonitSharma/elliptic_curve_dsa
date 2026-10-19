"""Freeze the small candidate and run one final, predeclared paired gate.

User authorized submission on 2026-10-19 with model GPT-6 Astra. This gate
does not itself search nonces or upload. Its verdict must never be resampled.
"""
import concurrent.futures
import hashlib
import json
import math
import statistics
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
out = root / 'parent4-qualification'
out.mkdir(exist_ok=False)
tree = root / 'candidate-parent4'
base = '0c3a0751ab66bd9144358d67563bcb79201cf636'
label = 'pareto-parent4-gate-20261019-v1'
batches = 32768

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(name, data):
    (out / name).write_text(json.dumps(data, indent=2) + '\n')

def git(*args):
    return subprocess.check_output(['git', '-C', str(tree), *args])

assert git('rev-parse', 'HEAD').decode().strip() == base
changed = git('diff', '--name-only', 'HEAD').decode().splitlines()
untracked = git('ls-files', '--others', '--exclude-standard').decode().splitlines()
assert all(p.startswith('src/point_add/') for p in changed + untracked)
tracked = git('ls-files').decode().splitlines()
protected = {}
for p in tracked:
    if not p.startswith('src/point_add/'):
        assert (tree / p).read_bytes() == git('show', base + ':' + p), p
        protected[p] = sha(tree / p)
source = {str(p.relative_to(tree)): sha(p) for p in (tree / 'src/point_add').rglob('*') if p.is_file()}
assert source['src/point_add/retained_product_pareto.rs'] == '683d659d3f6661c8633ed169b0bea5a951d4a9b8fffddf7c0946e94d76dbcb89'
patch = git('diff', '--binary', 'HEAD')
assert hashlib.sha256(patch).hexdigest() == '98a0801509ecb370f3bb7708d6f00a2a126e6de5e69f05cdffcc68f0e64c7082'
(out / 'tracked.patch').write_bytes(patch)
save('protected-files.json', protected)
save('point-add-source.json', source)
subprocess.run(['tar', '-czf', str(out / 'point-add-source.tar.gz'), '-C', str(tree), 'src/point_add'], check=True)
native = json.loads((root / 'NATIVE-PILOT.json').read_text())
assert native['status'] == 'NATIVE_PILOT_BYTE_IDENTITY_PASS'
assert (root / 'native-pilot.exit').read_text().strip() == '0'
api = 'https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions'
data = urllib.request.urlopen(api, timeout=60).read()
(out / 'public-submissions.json').write_bytes(data)
records = json.loads(data)['submissions']
eligible = [r for r in records if
    (r.get('status') == 'accepted' or (r.get('status') == 'rejected' and r.get('rejectionReason') == 'score did not improve current best'))
    and isinstance(r.get('officialScore'), int) and r['officialScore'] > 0
    and (r.get('officialMetrics') or {}).get('qubits', 0) * (r.get('officialMetrics') or {}).get('toffoli', 0) == r['officialScore']]
leader = min(eligible, key=lambda r: r['officialScore'])
save('public-parent.json', leader)
assert leader['id'] == '9dc3798c-93e0-4da4-a6a9-37586737c4af', 'Public parent changed; no gate started'
binary = Path('/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2')
assert sha(binary) == '790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
paths = {'parent': root / 'parent/ops.bin', 'candidate': tree / 'ops.bin'}
assert sha(paths['parent']) == '99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
assert sha(paths['candidate']) == native['stream_sha256'] == '9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'
available = int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))) * 1024
assert available > 180 * 1024**3, 'Insufficient headroom; census not started'
decl = {'declared_at_utc': datetime.now(timezone.utc).isoformat(), 'label': label,
    'batch_count': batches, 'shots_per_batch': 64, 'workers_per_stream': 16,
    'public_parent': leader['id'], 'base_revision': base,
    'streams': {k: {'path': str(p), 'sha256': sha(p)} for k, p in paths.items()},
    'driver_sha256': sha(__file__), 'point_add_manifest_sha256': sha(out / 'point-add-source.json'),
    'verdict_is_final': True, 'submission_authorized': True, 'model_attribution': 'GPT-6 Astra',
    'harness': 'Codex', 'nonce_search_started': False,
    'required_rules': ['candidate value shots <= parent', 'one-sided exact McNemar p >= 0.05', '141 * candidate failed batches / total <= 18', 'zero dirty shots']}
save('DECLARATION.json', decl)
print(json.dumps(decl, indent=2), flush=True)

def census(item):
    key, path = item
    with (out / (key + '.log')).open('wb') as log:
        subprocess.run([str(binary), str(path), label, '0', str(batches), '16', str(out / (key + '.jsonl')), '0'], stdout=log, stderr=subprocess.STDOUT, check=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(census, paths.items()))
rows = {}
for key in paths:
    a = [json.loads(line) for line in (out / (key + '.jsonl')).open()]
    assert len(a) == batches
    rows[key] = {r['batch']: r for r in a}
    assert sorted(rows[key]) == list(range(batches))
    assert all(r['shots'] == 64 and r.get('skipped', 0) == 0 for r in a)
p, c = rows['parent'], rows['candidate']
failed = {k: sum(bool(r['failures']) for r in a.values()) for k, a in rows.items()}
value = {k: sum(r['value_shots'] for r in a.values()) for k, a in rows.items()}
dirty = {k: sum(r['dirty_shots'] for r in a.values()) for k, a in rows.items()}
b = sum(bool(c[i]['failures']) and not p[i]['failures'] for i in p)
new_pass = sum(bool(p[i]['failures']) and not c[i]['failures'] for i in p)
prob = sum(math.comb(b + new_pass, x) for x in range(b, b + new_pass + 1)) / 2**(b + new_pass)
rules = {'value_not_above_parent': value['candidate'] <= value['parent'],
    'paired_mcnemar_p_at_least_005': prob >= .05,
    'failed_batches_per_packet_at_most_18': 141 * failed['candidate'] / batches <= 18,
    'zero_dirty_shots': dirty['candidate'] == 0}
delta = [(p[i]['toffoli'] - c[i]['toffoli']) / 64 for i in p]
result = {'status': 'FAILURE_GATE_PASS' if all(rules.values()) else 'FAILURE_GATE_FAIL',
    'label': label, 'batches': batches, 'shots_each': 64 * batches, 'rules': rules,
    'failed_batches': failed, 'value_shots': value, 'dirty_shots': dirty,
    'newly_failing_b': b, 'newly_passing_c': new_pass, 'mcnemar_one_sided_p': prob,
    'failed_batches_per_packet': {k: 141 * v / batches for k, v in failed.items()},
    'paired_mean_toffoli_saving': statistics.mean(delta),
    'saving_standard_error': statistics.stdev(delta) / batches**.5,
    'mean_toffoli': {k: sum(r['toffoli'] for r in a.values()) / (64 * batches) for k, a in rows.items()},
    'census_sha256': {k: sha(out / (k + '.jsonl')) for k in paths},
    'stream_sha256': {k: sha(path) for k, path in paths.items()},
    'no_official_benchmark_or_nonce_search': True}
assert all(sha(tree / p) == h for p, h in {**source, **protected}.items())
assert all(sha(path) == decl['streams'][key]['sha256'] for key, path in paths.items())
save('RESULT.json', result)
print(json.dumps(result, indent=2), flush=True)
assert all(rules.values()), 'Final gate failed; never rerun to reverse the verdict'
