"""External, unscored census of measurement erasure after bound rewrites."""
from pathlib import Path
import subprocess
import sys

base, dest, helper = map(Path, sys.argv[1:])
subprocess.run([sys.executable, str(helper), str(base), str(dest)], check=True)
(dest/'src/cond_pass.rs').write_bytes((base/'src/point_add/cond_pass.rs').read_bytes())
p = dest/'src/main.rs'
s = p.read_text().replace('mod affine_simplify;', 'mod affine_simplify;\nmod cond_pass;')
needle = '    truth_simplify::audit_zero(&ops,args[2].parse().unwrap());'
assert s.count(needle) == 1
s = s.replace(needle, r'''
    std::env::set_var("SL_COND", &args[2]);
    std::env::set_var("SL_COND_RVDIAG", "1");
    let before=ops.iter().filter(|o| matches!(o.kind,K::CCX|K::CCZ)).count();
    let ops=cond_pass::run(ops);
    let after=ops.iter().filter(|o| matches!(o.kind,K::CCX|K::CCZ)).count();
    println!("ERASE_AUDIT emitted_before={before} emitted_after={after} removed={} ops={}",before-after,ops.len());
''')
p.write_text(s)
p=dest/'Cargo.toml';p.write_text(p.read_text().replace('name="wire_zero_audit"', 'name="erase_audit"'))
