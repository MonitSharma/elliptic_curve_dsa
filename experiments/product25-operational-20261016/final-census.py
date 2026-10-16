"""Run the predeclared final cohort once, after unchanged native benchmark.

All rows are retained. This research coordinator never changes a candidate,
selects a nonce, submits a result, or accepts a partial census.
"""
from pathlib import Path
import datetime, hashlib, json, math, subprocess, sys

ROOT = Path('/home/hclau/ecdsa_research')
HERE = ROOT / 'product25-final-20261016'
OPERATIONAL = ROOT / 'product25-operational-20261016'
TREE = HERE / 'candidate'
ROLES = ['parent', 'candidate']
RUNNER_SHA = '790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
PARENT_SHA = '2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
LABEL = 'product25-final-nonce-20261016-v1'

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def write(path, value):
    assert not path.exists(), f'refuse overwrite: {path}'
    path.write_text(json.dumps(value, indent=2) + '\n')

def source_pins():
    paths = subprocess.check_output(['git', '-C', str(TREE), 'ls-files'], text=True).splitlines()
    protected = {}
    for name in paths:
        if name.startswith('src/point_add/'):
            continue
        raw = (TREE / name).read_bytes()
        assert raw == subprocess.check_output(['git', '-C', str(TREE), 'show', 'HEAD:' + name]), name
        protected[name] = hashlib.sha256(raw).hexdigest()
    assert len(protected) == 17
    source = {str(p.relative_to(TREE)): digest(p) for p in (TREE / 'src/point_add').rglob('*') if p.is_file()}
    changed = subprocess.check_output(['git', '-C', str(TREE), 'diff', '--name-only', 'HEAD'], text=True).splitlines()
    assert all(name.startswith('src/point_add/') for name in changed), changed
    return dict(source=source, protected=protected, changed=changed)

def read_rows(path):
    rows = {}
    with path.open() as f:
        for line in f:
            assert line.endswith('\n')
            row = json.loads(line)
            batch = row['batch']
            assert type(batch) is int and 0 <= batch < 32768 and batch not in rows
            assert row['shots'] == 64 and type(row['toffoli']) is int and row['toffoli'] >= 0
            failures = row['failures']
            lanes = [r['lane'] for r in failures]
            assert len(lanes) == len(set(lanes)) and all(type(i) is int and 0 <= i < 64 for i in lanes)
            for kind in ['value', 'phase', 'dirty']:
                assert sum(bool(r.get(kind, False)) for r in failures) == row[kind + '_shots']
            rows[batch] = row
    assert len(rows) == 32768 and set(rows) == set(range(32768))
    return rows

def summarize(rows):
    total = sum(r['toffoli'] for r in rows.values())
    failed = sum(bool(r['failures']) for r in rows.values())
    return dict(batches=len(rows), shots=64 * len(rows), failed_batches=failed,
                failed_shots=sum(len(r['failures']) for r in rows.values()),
                lambda_failed_batches_per9024=141 * failed / len(rows),
                toffoli_total=total, mean_executed_toffoli=total / (64 * len(rows)),
                **{kind + '_shots': sum(r[kind + '_shots'] for r in rows.values()) for kind in ['value', 'phase', 'dirty']})

def main():
    expected_candidate_sha = sys.argv[1]
    assert len(expected_candidate_sha) == 64
    plan_path = OPERATIONAL / 'FINAL-CENSUS-PLAN.json'
    plan = json.loads(plan_path.read_text())
    assert plan['label'] == LABEL and plan['first_batch'] == 0
    assert plan['batches_per_source'] == 32768 and plan['workers_per_source'] == 4
    assert plan['shots_per_source'] == 2097152 and plan['runner_sha256'] == RUNNER_SHA
    assert plan['parent_stream'] == PARENT_SHA
    audit_path = OPERATIONAL / 'ROOT_TERMINAL_AUDIT.json'
    audit = json.loads(audit_path.read_text())
    assert audit['status'] == 'LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS'
    assert audit['lowest_full_protected_pass'] == 47449113
    benchmark_path = HERE / 'BENCHMARK_RESULT.json'
    benchmark = json.loads(benchmark_path.read_text())
    assert benchmark['status'] == 'UNCHANGED_BENCHMARK_PASS'
    assert benchmark['candidate_stream_sha256'] == expected_candidate_sha
    assert benchmark['qubits'] == 1234 and benchmark['product'] < 939347948
    freeze_path = HERE / 'SOURCE_FREEZE.json'
    native_path = HERE / 'NATIVE_RECEIPT.json'
    freeze = json.loads(freeze_path.read_text())
    native = json.loads(native_path.read_text())
    assert digest(freeze_path) == 'eae8505df54f5d90240155b936c08a8baca7278a40dd8a54ef9904dcd621d477'
    assert native['status'] == 'NATIVE_SELECTED_NONCE_PREFIX_AND_TAIL_PASS'
    assert native['pre_tail_byte_identical'] and native['tail_is_48_unconditional_xx_pairs']
    assert native['tail_nonce'] == 47449113 and native['candidate_stream_sha256'] == expected_candidate_sha
    assert benchmark['native_receipt_sha256'] == digest(native_path)
    assert benchmark['source_freeze_sha256'] == native['source_freeze_sha256'] == digest(freeze_path)
    assert benchmark['score_sha256'] == digest(HERE / 'score.json')
    assert benchmark['tested_shots'] == 9024
    assert all(benchmark[k] == 0 for k in ['classical_mismatches', 'phase_garbage_batches', 'ancilla_garbage_batches'])
    runner = Path(plan['runner'])
    sources = dict(parent=ROOT / 'product-exact-20261015/tip/ops.bin', candidate=TREE / 'ops.bin')
    expected = dict(parent=PARENT_SHA, candidate=expected_candidate_sha)
    assert digest(runner) == RUNNER_SHA
    assert {role: digest(path) for role, path in sources.items()} == expected
    pins = source_pins()
    assert pins['source'] == freeze['source_files'] and pins['protected'] == freeze['protected_files']
    preflight = json.loads(subprocess.check_output(['python3', str(ROOT / 'server-preflight.py')]))
    assert preflight['hostname'] == 'LHC-104-070'
    assert preflight['memory']['MemAvailable_bytes'] > 110 * 1024**3
    dest = HERE / 'final-fresh'
    dest.mkdir(exist_ok=False)
    binding = dict(status='FIXED_FINAL_COHORT_BOUND_BEFORE_ANY_ROWS', label=LABEL,
                   first_batch=0, batches_per_source=32768, workers_per_source=4,
                   source_paths={k: str(v) for k, v in sources.items()}, source_sha256=expected,
                   runner_sha256=RUNNER_SHA, plan_sha256=digest(plan_path),
                   terminal_audit_sha256=digest(audit_path), benchmark_receipt_sha256=digest(benchmark_path),
                   native_receipt_sha256=digest(native_path), source_freeze_sha256=digest(freeze_path),
                   native_source_pins=pins, preflight=preflight,
                   launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   coordinator_sha256=digest(Path(__file__)), no_resampling=True, submission_mode='queue')
    write(HERE / 'FINAL_CENSUS_BINDING.json', binding)
    jobs = []
    logs = []
    for role in ROLES:
        log = (dest / (role + '.log')).open('x')
        logs.append(log)
        command = [str(runner), str(sources[role]), LABEL, '0', '32768', '4', str(dest / (role + '.jsonl')), '0']
        job = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        jobs.append(job)
        (dest / (role + '.pid')).write_text(str(job.pid) + '\n')
    codes = [job.wait() for job in jobs]
    for role, code, log in zip(ROLES, codes, logs):
        (dest / (role + '.exit')).write_text(str(code) + '\n')
        log.close()
    assert codes == [0, 0], codes
    assert source_pins() == pins
    assert {role: digest(path) for role, path in sources.items()} == expected
    assert digest(runner) == RUNNER_SHA
    assert digest(plan_path) == binding['plan_sha256']
    assert digest(audit_path) == binding['terminal_audit_sha256']
    assert digest(benchmark_path) == binding['benchmark_receipt_sha256']
    assert digest(native_path) == binding['native_receipt_sha256']
    assert digest(freeze_path) == binding['source_freeze_sha256']
    data = {role: read_rows(dest / (role + '.jsonl')) for role in ROLES}
    summary = {role: summarize(data[role]) for role in ROLES}
    a, b = data['parent'], data['candidate']
    for batch in range(32768):
        assert a[batch]['skipped'] == b[batch]['skipped']
        fa = {r['lane']: r for r in a[batch]['failures']}
        fb = {r['lane']: r for r in b[batch]['failures']}
        for lane in fa.keys() & fb.keys():
            assert (fa[lane]['k1'], fa[lane]['k2']) == (fb[lane]['k1'], fb[lane]['k2'])
    delta = [(a[i]['toffoli'] - b[i]['toffoli']) / 64 for i in range(32768)]
    mean = sum(delta) / len(delta)
    passed = (summary['candidate']['failed_batches'] <= summary['parent']['failed_batches']
              and summary['candidate']['lambda_failed_batches_per9024'] <= 18
              and summary['candidate']['dirty_shots'] == 0)
    result = dict(status='FINAL_FRESH_CENSUS_PASS' if passed else 'FINAL_FRESH_CENSUS_FAIL',
                  failure_gate_pass=passed, label=LABEL, cohorts=summary,
                  paired_mean_T_saving=mean,
                  paired_saving_standard_error=math.sqrt(sum((x - mean)**2 for x in delta) / (len(delta) * (len(delta) - 1))),
                  newly_passing_batches=sum(bool(a[i]['failures']) and not b[i]['failures'] for i in a),
                  newly_failing_batches=sum(bool(b[i]['failures']) and not a[i]['failures'] for i in a),
                  source_sha256=expected, raw_row_sha256={r: digest(dest / (r + '.jsonl')) for r in ROLES},
                  binding_sha256=digest(HERE / 'FINAL_CENSUS_BINDING.json'),
                  all_rows_included=True, no_resampling=True, submission_mode='queue',
                  public_submission_performed=False)
    write(HERE / 'FINAL_CENSUS_RESULT.json', result)
    print(json.dumps(result, indent=2))
    assert passed, 'Final failure gate failed; preserve candidate and all rows without a new sample'

if __name__ == '__main__':
    main()
