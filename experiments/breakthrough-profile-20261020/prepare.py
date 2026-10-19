"""Create a detached diagnostic observer; preserve the accepted source tree."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WS = ROOT.parent
TREE = ROOT / 'observer'
BASE = '90e777ea8242faa0acb2462c5cb5be7c318a2d64'
REPO = WS / 'toffoli'

def run(*args):
    return subprocess.check_output(args)

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

assert not TREE.exists(), 'Never overwrite an existing observer'
run('git', '-C', str(REPO), 'fetch', 'origin', BASE)
run('git', '-C', str(REPO), 'worktree', 'add', '--detach', str(TREE), BASE)
assert not run('git', '-C', str(TREE), 'status', '--porcelain').strip()
protected = {name: sha(TREE / name) for name in run('git', '-C', str(TREE), 'ls-files').decode().splitlines()
             if not name.startswith('src/point_add/')}
assert len(protected) == 17

def replace(path, old, new):
    raw = path.read_bytes()
    assert raw.count(old) == 1, (path, raw.count(old))
    path.write_bytes(raw.replace(old, new))

# Avoid enabling report_totals(), which other research code may consult.
# Observe already-maintained counters only; no operation is inserted.
replace(TREE / 'src/point_add/builder.rs', b'fn report_phase(&mut self) {', b'''fn report_phase(&mut self) {
        eprintln!("BREAK_PHASE\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}", self.phase,
            self.ops.len(), self.active_qubits, self.peak_qubits,
            self.phase_kind_ops[OperationType::CCX as usize],
            self.phase_kind_ops[OperationType::CCZ as usize]);''')

# Existing PeakCensus observes live owners; force its constructor on without
# enabling any arithmetic or recipe research overlay.
path = TREE / 'src/point_add/record.rs'
raw = path.read_bytes()
start = raw.index(b'impl PeakCensus {')
begin = raw.index(b'    pub fn new() -> Self {', start)
end = raw.index(b'    /// Checked at the call site', begin)
raw = raw[:begin] + b'''    pub fn new() -> Self {
        Self { enabled: true, op_lo: 0, op_hi: usize::MAX, ..Self::default() }
    }

''' + raw[end:]
path.write_bytes(raw)

replace(TREE / 'src/point_add/mod.rs', b'let mut ops = build_point_add();',
        b'let mut ops = build_point_add();\n    break_profile::save_ops("prepass.ops.bin", &ops);')
with (TREE / 'src/point_add/mod.rs').open('ab') as f:
    f.write(b'\nmod break_profile;\n')
writer = (WS / 'product-carry-readers-20261019/io.rs').read_text()
writer = writer.replace('use quantum_ecc::circuit::', 'use crate::circuit::', 1)
(TREE / 'src/point_add/break_profile.rs').write_text(writer)
assert all(sha(TREE / name) == digest for name, digest in protected.items())
(ROOT / 'observer-source.patch').write_bytes(run('git', '-C', str(TREE), 'diff', '--binary', 'HEAD'))
freeze = {'status': 'DIAGNOSTIC_ONLY_NO_CANDIDATE_GATE_NONCE_OR_SCORE', 'base': BASE,
          'expected_final_stream_sha256': '125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501',
          'protected_files': protected,
          'source_files': {p.relative_to(TREE).as_posix(): sha(p)
                           for p in sorted((TREE / 'src/point_add').rglob('*')) if p.is_file()}}
(ROOT / 'SOURCE_FREEZE.json').write_text(json.dumps(freeze, indent=2) + '\n')
print('Diagnostic observer prepared; all protected files unchanged.', flush=True)
