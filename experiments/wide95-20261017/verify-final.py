"""Verify the WIDE95 final source: only point_add changed, protected files intact, pre-tail
identical to the frozen gated stream, tail encodes the selected nonce, and record the score."""
from pathlib import Path
import ctypes, ctypes.util, hashlib, json, re, struct, subprocess, urllib.request
root = Path('/home/hclau/ecdsa_research/wide95-native-20261017'); e = root / 'evidence'; tree = root / 'candidate'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
protected = json.loads((root / 'protected.json').read_text())
for p, h in protected.items(): assert sha(tree / p) == h, p
changed = subprocess.check_output(['git', '-C', str(tree), 'diff', '--name-only', 'HEAD'], text=True).splitlines()
assert changed and all(p.startswith('src/point_add/') for p in changed), changed
z = ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]; z.ZSTD_decompress.restype = ctypes.c_size_t
def decode(p):
    d = Path(p).read_bytes(); assert d[:8] == b'QECCOPSZ'; n = struct.unpack_from('<Q', d, 8)[0]
    out = ctypes.create_string_buffer(n * 56); assert z.ZSTD_decompress(out, len(out), d[16:], len(d) - 16) == n * 56
    return n, out.raw
n, final = decode(tree / 'ops.bin'); n0, frozen = decode(e / 'frozen-ops.bin'); assert n == n0
end = (n - 96) * 56; assert final[:end] == frozen[:end]
k = json.loads((e / 'selection.json').read_text())['nonce']; absent = 2 ** 64 - 1
for bit in range(48):
    for pair in range(2):
        assert struct.unpack_from('<7Q', final, end + (2 * bit + pair) * 56) == (6, absent, absent, (k >> bit) & 1, absent, absent, absent)
log = (e / 'benchmark.log').read_text()
assert 'all 9024 shots OK' in log and '=== experiment OK ===' in log
score = json.loads((e / 'score.json').read_text())
total = int(re.findall(r'total Toffoli \(sum\)\s*:\s*(\d+) over 9024 shots', log)[0])
try:
    with urllib.request.urlopen('https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions', timeout=60) as r:
        subs = json.load(r)['submissions']
    ev = [s for s in subs if s.get('officialMetrics') and (s['status'] == 'accepted' or s.get('rejectionReason') == 'score did not improve current best')]
    best_t = min(s['officialMetrics']['toffoli'] for s in ev)
except Exception as x:
    best_t = None
subprocess.run(['git', '-C', str(tree), 'add', '--intent-to-add', 'src/point_add'], check=True)
(e / 'final-candidate.patch').write_bytes(subprocess.check_output(['git', '-C', str(tree), 'diff', '--binary', 'HEAD', '--', 'src/point_add']))
res = {'status': 'UNCHANGED_BENCHMARK_PASS', 'qubits': score['metrics']['qubits'], 'rounded_mean_toffoli': score['metrics']['toffoli'],
       'product': score['score'], 'total_executed_toffoli': total, 'mean_executed_toffoli': total / 9024, 'nonce': k,
       'final_stream_sha256': sha(tree / 'ops.bin'), 'pre_tail_identical_to_gated_stream': True,
       'public_min_toffoli_at_check': best_t, 'beats_public_toffoli_record': best_t is not None and score['metrics']['toffoli'] < best_t,
       'patch_sha256': sha(e / 'final-candidate.patch'), 'submission_mode': 'queue'}
(root / 'BENCHMARK_RESULT.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res, indent=2))
