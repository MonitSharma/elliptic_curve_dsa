from pathlib import Path
import subprocess
import sys
base,dest,helper=map(Path,sys.argv[1:])
subprocess.run([sys.executable,str(helper),str(base),str(dest)],check=True)
(dest/'src/pebble_audit.rs').write_bytes(Path(__file__).with_name('pebble_audit.rs').read_bytes())
query=Path(__file__).with_name('affine_pebble_query.rs').read_text()
(dest/'src/interned_witness.rs').write_text((base/'src/point_add/interned_witness.rs').read_text()+query)
p=dest/'src/main.rs';s=p.read_text().replace('mod affine_simplify;','mod affine_simplify;\nmod pebble_audit;\nmod interned_witness;')
s=s.replace('    truth_simplify::audit_zero(&ops,args[2].parse().unwrap());','    pebble_audit::audit(&ops);')
p.write_text(s)
p=dest/'Cargo.toml';p.write_text(p.read_text().replace('name="wire_zero_audit"','name="pebble_audit"'))
