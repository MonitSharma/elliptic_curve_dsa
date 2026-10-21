"""Keep the failed 32-GiB proof attempt; reduce only symbolic expression cap."""
import hashlib, json, shutil
from pathlib import Path
r = Path(__file__).resolve().parent
old = r / 'parent4-transfer'
new = r / 'parent4-transfer-v2'
prior_exit = old / 'parent4-transfer.exit'
assert prior_exit.exists()
assert not (old / 'PUBLIC-PARENT-TRANSFER.json').exists()
assert 'memory allocation' in (old / 'verify.log').read_text()
new.mkdir(exist_ok=False)
for name in ['Cargo.toml', 'Cargo.lock', 'io.rs', 'leases.json']:
    shutil.copyfile(old / name, new / name)
source = (old / 'verify.rs').read_text()
assert source.count('8192);') == 2
(new / 'verify.rs').write_text(source.replace('8192);', '1024);'))
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in new.iterdir() if p.is_file()}
(new / 'PROOF-SOURCE.json').write_text(json.dumps(manifest, indent=2) + '\n')
(new / 'RETRY.json').write_text(json.dumps({'reason': 'First proof hit its 32-GiB address-space cap',
    'prior_exit': prior_exit.read_text().strip(),
    'change': 'Exact-expression cap 8192 -> 1024; truncation produces fresh independent symbols, never a presumed equality.',
    'circuit_changed': False, 'statistical_gate_rerun': False}, indent=2) + '\n')
