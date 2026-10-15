"""Observation-only reset provenance; protected simulator stays unchanged."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parent
source = root / 'diagnostic-b3'
dest = root / 'diagnostic-reset-b3'
rev = 'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
assert not dest.exists()
subprocess.run(['git', 'clone', '--shared', '--no-checkout', str(source), str(dest)], check=True)
subprocess.run(['git', '-C', str(dest), 'checkout', '--detach', rev], check=True)
base = dest / 'src/point_add'
(base / 'reset_trace.rs').write_bytes((root / 'reset_trace.rs').read_bytes())
s = (dest / 'src/sim.rs').read_text()
needle = "    pub fn apply_iter<'b>(&mut self, ops: impl Iterator<Item = &'b Op>) {"
assert s.count(needle) == 1
s = s.replace(needle, needle + '\n        self.apply_observed(ops, |_,_,_,_| {});\n    }\n    pub fn apply_observed<\'b>(&mut self, ops: impl Iterator<Item = &\'b Op>, mut observe: impl FnMut(usize, &Self, &Op, u64)) {')
s = s.replace('for op in ops {', 'for (op_index, op) in ops.enumerate() {')
s = s.replace('            let executed_shots = cond.count_ones() as u64;', '            observe(op_index, self, op, cond);\n            let executed_shots = cond.count_ones() as u64;')
(base / 'observed_sim.rs').write_text(s)
p = base / 'builder.rs'
s = p.read_text()
needle = '    pub fn free(&mut self, q: QubitId) {'
assert s.count(needle) == 1
s = s.replace(needle, '    #[track_caller]\n' + needle + '\n        super::reset_trace::record(self.ops.len(), self.phase, std::panic::Location::caller());')
s = s.replace('    pub fn free_vec(&mut self, qs: &[QubitId]) {', '    #[track_caller]\n    pub fn free_vec(&mut self, qs: &[QubitId]) {')
p.write_text(s)
p = base / 'mod.rs'
s = p.read_text()
needle = '    let mut ops = build_point_add();'
assert s.count(needle) == 1
s = 'mod reset_trace;\nmod observed_sim;\n' + s.replace(needle, needle + '\n    reset_trace::run(&ops);\n    return ops;')
p.write_text(s)
patch = subprocess.check_output(['git', '-C', str(dest), 'diff', '--binary'])
(root / 'reset-tracked.patch').write_bytes(patch)
manifest = {'status': 'diagnostic-only', 'source_revision': rev,
            'purpose': 'Locate nonzero reset operands, with exact full-state parity against protected simulator.',
            'patch_sha256': hashlib.sha256(patch).hexdigest(),
            'diagnostic_sources': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [base/'reset_trace.rs', base/'observed_sim.rs']}}
(root / 'reset-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
