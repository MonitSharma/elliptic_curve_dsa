"""Gate-inert fold-entry/exit tracing; all source changes remain in point_add."""
from pathlib import Path
import argparse

p = argparse.ArgumentParser()
p.add_argument("source", type=Path)
p.add_argument("output", type=Path)
p.add_argument("--candidate", action="store_true")
a = p.parse_args()
s = a.source.read_text()
signature = "fn fold_fwd_v2(c: &mut Builder, acc: &[QubitId], e: [QubitId; 3], nm: [QubitId; 3], k1: QubitId, k2: QubitId, fin: usize, mut esh: Option<&mut ESh>, ttm: bool, drop: usize) -> Vec<usize> {"
assert s.count(signature) == 1
entry = '''
    let product_fold_at = PAYLOAD_AT.with(|x|x.get());
    let product_fold_start = c.op_count();
    eprintln!("PRODUCT_FOLD_ENTRY payload={:?} fin={} ttm={} drop={} op={} acc={:?} e={:?} nm={:?} k={:?} state={:?} dims={:?}", product_fold_at, fin, ttm, drop, product_fold_start, acc.iter().map(|q|q.0).collect::<Vec<_>>(), e.map(|q|q.0), nm.map(|q|q.0), [k1.0,k2.0], c.y42_alloc_state(), c.i13_dims());
'''
s = s.replace(signature, signature + entry)
start = s.index(signature)
end = s.index("/// The borrow into bit", start)
part = s[start:end]
exit_log = '''    eprintln!("PRODUCT_FOLD_EXIT payload={:?} fin={} ttm={} drop={} start={} op={} plan={:?} state={:?} dims={:?}", product_fold_at, fin, ttm, drop, product_fold_start, c.op_count(), plan, c.y42_alloc_state(), c.i13_dims());
'''
assert part.count("    plan\n}") == 1
part = part.replace("    plan\n}", exit_log + "    plan\n}")
if a.candidate:
    old = "LOAN_ACTIVE.with(|x|x.set(false));return plan;"
    assert part.count(old) == 1
    part = part.replace(old, "LOAN_ACTIVE.with(|x|x.set(false));\n" + exit_log + "        return plan;")
s = s[:start] + part + s[end:]
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(s, newline="\n")
