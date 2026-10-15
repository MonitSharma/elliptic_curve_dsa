"""Re-run existing exact simplifiers after public fingerprint-bound rewrites.

External diagnostic only: candidate and protected source files remain unchanged.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

base,dest=map(Path,sys.argv[1:3])
helper=Path(__file__).with_name('prepare-wire-zero-audit.py')
subprocess.run([sys.executable,str(helper),str(base),str(dest)],check=True)
(dest/'src/interned_witness.rs').write_bytes((base/'src/point_add/interned_witness.rs').read_bytes())
p=dest/'src/main.rs';s=p.read_text().replace('mod affine_simplify;','mod affine_simplify;\nmod interned_witness;')
needle='    truth_simplify::audit_zero(&ops,args[2].parse().unwrap());'
assert s.count(needle)==1
s=s.replace(needle,r'''
    fn count(ops:&[Op])->usize {ops.iter().filter(|o|matches!(o.kind,K::CCX|K::CCZ)).count()}
    println!("FINAL_PASS baseline ops={} toffoli={}",ops.len(),count(&ops));
    for (name,pass) in [
        ("product",truth_simplify::simplify_products as fn(Vec<Op>)->Vec<Op>),
        ("affine",affine_simplify::simplify),
        ("quadratic",quadratic_simplify::simplify),
        ("truth",truth_simplify::simplify),
        ("interned",interned_witness::witnesses),
    ] {
        let before=count(&ops);ops=pass(ops);
        println!("FINAL_PASS {name} ops={} toffoli={} removed={}",ops.len(),count(&ops),before-count(&ops));
    }
    // No benchmark or score; record every changed operation by sequential match.
''')
p.write_text(s)
p=dest/'Cargo.toml';p.write_text(p.read_text().replace('name="wire_zero_audit"','name="final_pass_audit"'))
