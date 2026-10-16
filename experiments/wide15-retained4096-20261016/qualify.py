"""Admit the predeclared current-parent stage; no nonce or submission work."""
from pathlib import Path
import hashlib, json, math, os, re, subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARENT = ROOT / 'wide15-record-20261016/evidence/final-ops.bin'
CANDIDATE = HERE / 'candidate/ops.bin'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    path = HERE / name
    assert not path.exists(), name
    path.write_text(json.dumps(value, indent=2) + '\n')

def rows(role):
    out = {}
    for line in (HERE / ('fresh-' + role + '.jsonl')).read_text().splitlines():
        r = json.loads(line)
        assert type(r['batch']) is int and 0 <= r['batch'] < 32768 and r['batch'] not in out
        assert r['shots'] == 64 and type(r['toffoli']) is int
        assert len({f['lane'] for f in r['failures']}) == len(r['failures'])
        for kind in ['value', 'phase', 'dirty']:
            assert r[kind + '_shots'] == sum(bool(f.get(kind, False)) for f in r['failures'])
        out[r['batch']] = r
    assert len(out) == 32768
    return out

def summary(data):
    fail = sum(bool(r['failures']) for r in data.values())
    return dict(batches=len(data), shots=64 * len(data), failed_batches=fail,
                lambda_failed_batches_per9024=141 * fail / len(data),
                mean_T=sum(r['toffoli'] for r in data.values()) / (64 * len(data)),
                **{k + '_shots': sum(r[k + '_shots'] for r in data.values()) for k in ['value', 'phase', 'dirty']})

assert (HERE / 'native-launcher.exit').read_text().strip() == '0'
native = json.loads((HERE / 'NATIVE_RESULT.json').read_text())
assert native['status'] == 'FULL_NORMAL_NATIVE_ALL_OP_BYTES_AND_PROTECTED_SOURCE_PASS'
assert json.loads((HERE / 'PROOF_RESULT.json').read_text())['status'] == 'UNIVERSAL_PADDED_STAGE_PASS'
declaration = json.loads((HERE / 'DECLARATION.json').read_text())
assert sha(PARENT) == declaration['input_stream_sha256']
assert sha(CANDIDATE) == native['native_stream_sha256']
preflight = json.loads(subprocess.check_output(['python3', str(ROOT / 'server-preflight.py')]))
assert preflight['hostname'] == 'LHC-104-070' and preflight['memory']['MemAvailable_bytes'] > 110 * 1024**3
checker = ROOT / 'product-exact-20261015/target-anchored-replay/release/product_paired_diagnostic'
assert sha(checker) == 'b8e534ed907ac44b5d936c4731bdb48a201ba4fd9822c9325cdd27f72b51e19d'
manifest = HERE / 'anchored.manifest'
assert not manifest.exists()
manifest.write_text(str(PARENT) + ' =\n' + str(HERE / 'candidate.bin') + ' ' + str(HERE / 'generation.log') + '\n')
write('QUALIFICATION_BINDING.json', dict(status='BOUND_BEFORE_ANCHORED_OR_FRESH_EVALUATION',
      source_sha256=dict(parent=sha(PARENT), candidate=sha(CANDIDATE)),
      native_receipt_sha256=sha(HERE / 'NATIVE_RESULT.json'),
      native_source_freeze_sha256=sha(HERE / 'NATIVE_SOURCE_FREEZE.json'),
      declaration_sha256=sha(HERE / 'DECLARATION.json'), proof_receipt_sha256=sha(HERE / 'PROOF_RESULT.json'),
      checker_sha256=sha(checker), manifest_sha256=sha(manifest), preflight=preflight,
      fresh_gate=declaration['prospective_fresh_gate'], no_nonce_search=True))
for family in ['independent', 'structured']:
    log_path = HERE / ('anchored-' + family + '.log')
    with log_path.open('x') as log:
        subprocess.run([str(checker), str(PARENT), str(HERE / 'candidate.bin'), '+' + str(manifest),
                        family, str(HERE / ('anchored-' + family + '.tsv'))], stdout=log, stderr=subprocess.STDOUT, check=True)
    text = log_path.read_text()
    assert re.search(r'DIAGNOSTIC_ONLY shots=256 unequal_batches=0 ', text), text[-2000:]
    assert 'right_dirty_batches=0' in text
write('ANCHORED_RESULT.json', dict(status='ALL_512_FULL_STATE_PHASE_MR_AND_EXTRA_ANCILLAS_PASS',
      tool_sha256=sha(checker), source_sha256=dict(parent=sha(PARENT), candidate=sha(HERE / 'candidate.bin')),
      logs={f: sha(HERE / ('anchored-' + f + '.log')) for f in ['independent', 'structured']},
      not_a_fresh_failure_or_resource_score=True))
runner = Path(declaration['prospective_fresh_gate']['runner'])
assert sha(runner) == declaration['prospective_fresh_gate']['runner_sha256']
preflight = json.loads(subprocess.check_output(['python3', str(ROOT / 'server-preflight.py')]))
assert preflight['memory']['MemAvailable_bytes'] > 110 * 1024**3
write('FRESH_LAUNCH.json', dict(status='FIXED_COHORT_BEFORE_ROWS', preflight=preflight,
      label=declaration['prospective_fresh_gate']['label'], first_batch=0, batches_per_source=32768,
      workers_per_source=4, source_sha256=dict(parent=sha(PARENT), candidate=sha(CANDIDATE))))
jobs, logs = [], []
for role, ops in [('parent', PARENT), ('candidate', CANDIDATE)]:
    log = (HERE / ('fresh-' + role + '.log')).open('x')
    logs.append(log)
    job = subprocess.Popen([str(runner), str(ops), declaration['prospective_fresh_gate']['label'],
                            '0', '32768', '4', str(HERE / ('fresh-' + role + '.jsonl')), '0'],
                           stdout=log, stderr=subprocess.STDOUT)
    jobs.append(job)
    (HERE / ('fresh-' + role + '.pid')).write_text(str(job.pid) + '\n')
codes = [j.wait() for j in jobs]
for role, code, log in zip(['parent', 'candidate'], codes, logs):
    log.close()
    (HERE / ('fresh-' + role + '.exit')).write_text(str(code) + '\n')
assert codes == [0, 0]
assert sha(PARENT) == declaration['input_stream_sha256'] and sha(CANDIDATE) == native['native_stream_sha256']
subprocess.run(['python3', str(HERE / 'verify_native.py')], check=True)
data = {role: rows(role) for role in ['parent', 'candidate']}
for i in range(32768):
    assert data['parent'][i]['skipped'] == data['candidate'][i]['skipped']
stats = {r: summary(d) for r, d in data.items()}
delta = [(data['parent'][i]['toffoli'] - data['candidate'][i]['toffoli']) / 64 for i in range(32768)]
mean = sum(delta) / len(delta)
passed = (stats['candidate']['failed_batches'] <= stats['parent']['failed_batches']
          and stats['candidate']['lambda_failed_batches_per9024'] <= 18
          and stats['candidate']['dirty_shots'] == 0 and mean > 0)
result = dict(status='FIXED_FRESH_GATE_PASS' if passed else 'FIXED_FRESH_GATE_FAIL',
      gate_pass=passed, cohorts=stats, label=declaration['prospective_fresh_gate']['label'],
      paired_mean_T_saving=mean, paired_saving_SE=math.sqrt(sum((x - mean)**2 for x in delta) / (len(delta) * (len(delta) - 1))),
      raw_rows_sha256={r: sha(HERE / ('fresh-' + r + '.jsonl')) for r in data},
      all_rows_included=True, resampling=False, nonce_search=False, resource_score=None)
write('FRESH_RESULT.json', result)
print(json.dumps(result, indent=2))
