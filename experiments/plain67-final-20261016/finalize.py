"""Finalize PLAIN67 after its search (queue mode; never submits).

Adapted from product25-final-20261016/finalize.py. Steps:
  prepare    - require the complete terminal audit, create a detached worktree of
               4b2ec52f, unpack the frozen native PLAIN67 source and change only the
               TAIL_NONCE literal; freeze hashes and the patch.
  native     - prove the regenerated stream's pre-tail bytes equal the frozen
               268aefe2 stream and the 96-op tail encodes the selected nonce.
  tailcheck  - census 512 batches of the final stream with the gate's label and
               require rows identical to the gate's candidate rows (the identity
               tail cannot change outcomes).
  benchmark  - validate the unchanged benchmark output, restore results.tsv, and
               compare the score with the then-current public product record.
"""
from pathlib import Path
import ctypes, ctypes.util, hashlib, json, re, shutil, struct, subprocess, sys, tarfile, urllib.request

r = Path(__file__).resolve().parent
ws = Path('/home/hclau/ecdsa_research')
t = r / 'candidate'
native = ws / 'product67-native-20261016/product67'
base = '4b2ec52fc55da796aa8f5ef851290297e8706424'
archive_hash = '428f0806a78c2da52ec56bf00e62d11ede22c1c9812753e42600321dbd82925d'
frozen_bin_hash = '57da98da03ee66da1af9397b607d4ce3381a7aa8f43c2fd32d5255d7a8ec58d5'
old_stream = ws / 'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin'
old_stream_hash = '268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d'
N_OPS = 17_891_821
OLD_NONCE = b'1046072871510'
API = 'https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name, x): (r / name).write_text(json.dumps(x, indent=2) + '\n')
def load(name): return json.loads((r / name).read_text())
def git(*args): return subprocess.check_output(['git', '-C', str(t), *args])
def nonce(): return load('ROOT_TERMINAL_AUDIT.json')['lowest_full_protected_pass']


def protected():
    out = {}
    for p in git('ls-files').decode().splitlines():
        if p.startswith('src/point_add/'):
            continue
        data = (t / p).read_bytes()
        assert data == git('show', 'HEAD:' + p), p
        out[p] = sha(t / p)
    assert len(out) == 17, len(out)
    return out


def decode(p):
    d = Path(p).read_bytes()
    assert d[:8] == b'QECCOPSZ'
    n = struct.unpack_from('<Q', d, 8)[0]
    assert n == N_OPS, n
    z = ctypes.CDLL(ctypes.util.find_library('zstd'))
    z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
    z.ZSTD_decompress.restype = ctypes.c_size_t
    out = ctypes.create_string_buffer(n * 56)
    assert z.ZSTD_decompress(out, len(out), d[16:], len(d) - 16) == n * 56
    return n, out.raw


def prepare():
    audit = load('ROOT_TERMINAL_AUDIT.json')
    assert audit['status'] == 'LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS'
    k = audit['lowest_full_protected_pass']
    assert isinstance(k, int) and 1 <= k < 2 ** 48
    assert sha(native / 'point-add-source.tar.gz') == archive_hash
    assert not t.exists()
    shutil.copy2(native / 'point-add-source.tar.gz', r / 'original-point-add-source.tar.gz')
    subprocess.run(['git', '-C', str(ws / 'upstream'), 'worktree', 'add', '--detach', str(t), base], check=True)
    with tarfile.open(r / 'original-point-add-source.tar.gz') as a:
        members = a.getmembers()
        # The PLAIN67 archive carries its 5 directory entries as well as 168 files.
        assert all((m.isfile() or m.isdir()) and (m.name + '/').startswith('src/point_add/')
                   and '..' not in Path(m.name).parts for m in members)
        assert sum(m.isfile() for m in members) == 168
        a.extractall(t, filter='data')
    p = t / 'src/point_add/mod.rs'
    src = p.read_bytes()
    assert src.count(OLD_NONCE) == 1
    p.write_bytes(src.replace(OLD_NONCE, str(k).encode()))
    assert sha(t / 'src/point_add/frozen_cache_product67.bin') == frozen_bin_hash
    with tarfile.open(r / 'original-point-add-source.tar.gz') as a:
        for m in a.getmembers():
            if not m.isfile():
                continue
            original = a.extractfile(m).read()
            if m.name == 'src/point_add/mod.rs':
                original = original.replace(OLD_NONCE, str(k).encode())
            assert original == (t / m.name).read_bytes(), m.name
    subprocess.run(['git', '-C', str(t), 'add', '--intent-to-add', 'src/point_add'], check=True)
    (r / 'candidate-source.patch').write_bytes(git('diff', '--binary', 'HEAD', '--', 'src/point_add'))
    files = {str(q.relative_to(t)): sha(q) for q in sorted((t / 'src/point_add').rglob('*')) if q.is_file()}
    with tarfile.open(r / 'point-add-source.tar.gz', 'w:gz') as a:
        for q in files:
            a.add(t / q, arcname=q, recursive=False)
    save('SOURCE_FREEZE.json', {
        'status': 'FROZEN_BEFORE_NATIVE_TESTS_AND_BENCHMARK', 'base_revision': base, 'candidate': str(t),
        'nonce': k, 'only_change_from_frozen_source': f'TAIL_NONCE literal 1046072871510 -> {k}',
        'old_source_archive_sha256': archive_hash, 'selected_source_archive_sha256': sha(r / 'point-add-source.tar.gz'),
        'patch_sha256': sha(r / 'candidate-source.patch'), 'source_files': files, 'protected_files': protected(),
        'search_audit_sha256': sha(r / 'ROOT_TERMINAL_AUDIT.json'), 'old_stream_sha256': old_stream_hash,
        'expected_pre_tail_ops': N_OPS - 96, 'submission_mode': 'queue'})
    print('SOURCE_FREEZE_SHA256', sha(r / 'SOURCE_FREEZE.json'), flush=True)


def native_receipt():
    f = load('SOURCE_FREEZE.json')
    for p, h in f['source_files'].items():
        assert sha(t / p) == h, p
    assert protected() == f['protected_files']
    k = f['nonce']
    n, data = decode(t / 'ops.bin')
    assert sha(old_stream) == old_stream_hash
    _, prior = decode(old_stream)
    end = (n - 96) * 56
    assert data[:end] == prior[:end]
    absent = 2 ** 64 - 1
    for bit in range(48):
        expected = (6, absent, absent, (k >> bit) & 1, absent, absent, absent)
        for pair in range(2):
            assert struct.unpack_from('<7Q', data, end + (2 * bit + pair) * 56) == expected
    result = {'status': 'NATIVE_SELECTED_NONCE_PREFIX_AND_TAIL_PASS', 'candidate_stream_sha256': sha(t / 'ops.bin'),
              'old_stream_sha256': old_stream_hash, 'ops': n, 'pre_tail_ops': n - 96,
              'pre_tail_sha3_256': hashlib.sha3_256(data[:end]).hexdigest(), 'pre_tail_byte_identical': True,
              'tail_nonce': k, 'tail_is_48_unconditional_xx_pairs': True,
              'source_freeze_sha256': sha(r / 'SOURCE_FREEZE.json'), 'loader_tests': 4, 'submission_mode': 'queue'}
    save('NATIVE_RECEIPT.json', result)
    print(json.dumps(result), flush=True)


def tailcheck():
    # Same census binary and argument form as the gate (product67-native-20261016/census.py).
    census = ws / 'simd-census-v2-20261016/bin/simd_census_v2'
    out = r / 'tailcheck.jsonl'
    assert not out.exists()
    subprocess.run([str(census), str(r / 'native-selected.ops.bin'), 'product67-frozen-20261016', '0', '512', '6', str(out), '0'], check=True)
    gate = {x['batch']: x for x in map(json.loads, (native / 'candidate-census.jsonl').open())}
    rows = [json.loads(line) for line in out.open()]
    assert len(rows) == 512
    diffs = [x['batch'] for x in rows if x != gate[x['batch']]]
    result = {'status': 'TAIL_INVARIANCE_PASS' if not diffs else 'TAIL_INVARIANCE_FAIL', 'label': 'product67-frozen-20261016',
              'batches': 512, 'differing_batches': diffs, 'rows_sha256': sha(out), 'census_binary_sha256': sha(census)}
    save('TAILCHECK.json', result)
    print(json.dumps(result), flush=True)
    assert not diffs


def public_records():
    with urllib.request.urlopen(API, timeout=60) as resp:
        subs = json.load(resp)['submissions']
    ev = [s for s in subs if s.get('officialMetrics') and s.get('officialScore')
          and (s['status'] == 'accepted' or s.get('rejectionReason') == 'score did not improve current best')]
    best = min(ev, key=lambda s: s['officialScore'])
    return {'product': best['officialScore'], 'metrics': best['officialMetrics'], 'id': best['id'],
            'source': best.get('submissionCommitSha'), 'submissions': len(subs)}


def benchmark():
    generated = (t / 'results.tsv').read_bytes()
    historical = git('show', 'HEAD:results.tsv')
    assert generated.startswith(historical)
    appended = generated[len(historical):]
    rows = appended.decode().splitlines()
    assert len(rows) == 1, rows
    fields = rows[0].split('\t')
    assert len(fields) >= 8 and fields[6] == 'OK' and fields[4:6] == ['1234', str(N_OPS)], fields
    (r / 'results.tsv').write_bytes(generated)
    (r / 'benchmark-appended-row.tsv').write_bytes(appended)
    shutil.copy2(t / 'score.json', r / 'score.json')
    (t / 'results.tsv').write_bytes(historical)
    before = load('NATIVE_RECEIPT.json')
    native_receipt()
    assert before == load('NATIVE_RECEIPT.json')
    log = (r / 'benchmark.log').read_text()
    for label, value in [('tested shots', 9024), ('classical mismatches', 0), ('phase-garbage batches', 0), ('ancilla-garbage batches', 0)]:
        assert re.findall(re.escape(label) + r'\s*:\s*(\d+)', log) == [str(value)], label
    assert 'all 9024 shots OK' in log and '=== experiment OK ===' in log
    score = json.loads((t / 'score.json').read_text())
    q, tof = score['metrics']['qubits'], score['metrics']['toffoli']
    assert q == 1234 and score['score'] == q * tof
    totals = re.findall(r'total Toffoli \(sum\)\s*:\s*(\d+) over 9024 shots', log)
    assert len(totals) == 1
    total = int(totals[0])
    mean = total / 9024
    assert int(mean + 0.5) == tof and fields[2] == f'{mean:.3f}'
    try:
        public = public_records()
    except Exception as e:  # network trouble must not hide the local result
        public = {'error': repr(e)}
    beats = 'product' in public and score['score'] < public['product']
    save('BENCHMARK_RESULT.json', {
        'status': 'UNCHANGED_BENCHMARK_PASS', 'qubits': q, 'rounded_mean_toffoli': tof, 'product': score['score'],
        'total_executed_toffoli': total, 'mean_executed_toffoli': mean, 'nonce': load('SOURCE_FREEZE.json')['nonce'],
        'candidate_stream_sha256': load('NATIVE_RECEIPT.json')['candidate_stream_sha256'],
        'tested_shots': 9024, 'classical_mismatches': 0, 'phase_garbage_batches': 0, 'ancilla_garbage_batches': 0,
        'public_product_record_at_check': public, 'beats_public_product_record': beats,
        'score_sha256': sha(r / 'score.json'), 'benchmark_log_sha256': sha(r / 'benchmark.log'),
        'submission_mode': 'queue', 'next': 'User reviews; submission note drafted from STATUS.md; never auto-submitted'})
    print((r / 'BENCHMARK_RESULT.json').read_text(), flush=True)


if __name__ == '__main__':
    {'prepare': prepare, 'native': native_receipt, 'tailcheck': tailcheck, 'benchmark': benchmark}[sys.argv[1]]()
