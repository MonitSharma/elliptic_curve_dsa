"""Create an isolated, observation-only B3 stage diagnostic. Not a submission."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline')
REV = 'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
DEST = ROOT / 'diagnostic-b3'
assert subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip() == REV
assert not subprocess.check_output(['git', '-C', str(SOURCE), 'status', '--porcelain'])
assert not DEST.exists()
subprocess.run(['git', 'clone', '--shared', '--no-checkout', str(SOURCE), str(DEST)], check=True)
subprocess.run(['git', '-C', str(DEST), 'checkout', '--detach', REV], check=True)
(ROOT / 'packets').mkdir()
old = Path('/home/hclau/ecdsa_research/toffoli-readiness-20261015/replay')
for family in ['independent', 'structured', 'candidate']:
    (ROOT / 'packets' / (family + '.tsv')).write_bytes((old / (family + '.tsv')).read_bytes())
base = DEST / 'src/point_add'
(base / 'repair_trace.rs').write_bytes((ROOT / 'repair_trace.rs').read_bytes())
p = base / 'builder.rs'
s = p.read_text()
needle = '    pub fn set_phase(&mut self, p: &\'static str) {'
assert s.count(needle) == 1
s = s.replace(needle, needle + '\n        super::repair_trace::mark(p, self.ops.len());')
p.write_text(s)
p = base / 'mod.rs'
s = p.read_text()
needle = '    let mut ops = build_point_add();'
assert s.count(needle) == 1
s = 'mod repair_trace;\n' + s.replace(needle, needle + '\n    repair_trace::run(&ops, square::sub_square_offset());\n    return ops;')
p.write_text(s)
patch = subprocess.check_output(['git', '-C', str(DEST), 'diff', '--binary'])
(ROOT / 'diagnostic-tracked.patch').write_bytes(patch)
manifest = {'status': 'diagnostic-only', 'source_revision': REV,
            'purpose': 'Trace unchanged raw B3 arithmetic on preserved packets before simplification; never score raw counts.',
            'source_status_before': 'clean', 'patch_sha256': hashlib.sha256(patch).hexdigest(),
            'trace_sha256': hashlib.sha256((base / 'repair_trace.rs').read_bytes()).hexdigest(),
            'packet_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'packets').glob('*.tsv'))}}
(ROOT / 'diagnostic-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
