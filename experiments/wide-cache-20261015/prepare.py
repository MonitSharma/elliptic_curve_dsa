"""Port the exact wide cache after all original passes; preserve their limits."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
SERVER = ROOT.parent
PARENT = '5a7c390233c72133df9b591c92e43422c5892142'
DEST = ROOT / 'candidate'
subprocess.run(['git', '-C', str(SERVER/'toffoli'), 'worktree', 'add', '--detach', str(DEST), PARENT], check=True)
base = DEST/'src/point_add'
old = SERVER/'toffoli-readiness-20261015'
cache = (old/'candidate-wide-v1/src/point_add/lazy_cache.rs').read_text()
cache = cache.replace('super::interned_witness::Support', 'super::cache_support::Support')
(base/'lazy_cache.rs').write_text(cache)
support = (base/'interned_witness.rs').read_text()
support = support.replace('const ATOM_CAP: usize = 32;', 'const ATOM_CAP: usize = 128;')
support = support.replace('const PRODUCT_CAP: usize = 200_000;', 'const PRODUCT_CAP: usize = 1_000_000;')
query = (old/'prepare.py').read_text().split("query='''", 1)[1].split("'''", 1)[0]
(base/'cache_support.rs').write_text(support + query)
p = base/'mod.rs'
s = p.read_text()
needle = '    let nonce: u64 = required_env("TAIL_NONCE");'
assert s.count(needle) == 1
p.write_text('mod cache_support;\nmod lazy_cache;\n' + s.replace(needle, '    ops = lazy_cache::optimize(ops);\n' + needle))
changed = subprocess.check_output(['git','-C',str(DEST),'diff','--name-only'],text=True).splitlines()
assert all(p.startswith('src/point_add/') for p in changed)
print(DEST)
