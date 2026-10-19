"""Compose only structural screens after the complete AND integration passes."""
import json
from pathlib import Path
r=Path(__file__).resolve().parent;c=r.parent/'product-carry-readers-20261019'
assert (r/'control.exit').read_text().strip()=='0'
assert json.loads((r/'control.json').read_text())['status']=='PROTECTED_SIMULATOR_EVENT_SUBSEQUENCE_CONTROL_PASS'
record=json.loads((r/'absorbed.json').read_text())
s=(c/'scan.rs').read_text()
old='429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842'
assert s.count(old)==1
(r/'combo_scan.rs').write_text(s.replace(old,record['output_full_sha3_256']),encoding='utf-8',newline='\n')
for src,dst in [('detector.rs','detector.rs'),('peak_profile.rs','combo_peak.rs'),('cover.py','cover.py')]:
    (r/dst).write_bytes((c/src).read_bytes())
cargo=(r/'Cargo.toml').read_text()
assert 'name="and_combo_scan"' not in cargo
cargo+='\n[[bin]]\nname="and_combo_scan"\npath="combo_scan.rs"\n\n[[bin]]\nname="and_combo_peak"\npath="combo_peak.rs"\n'
(r/'Cargo.toml').write_text(cargo,encoding='utf-8',newline='\n')
