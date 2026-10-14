"""Prepare a precision repair in an isolated c95b9325 research checkout.

Only src/point_add changes. This does not fund QB24 or lower peak width.
The preserved compact source is copied before making the explicit K25 change.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

compact, dest = map(lambda s: Path(s).resolve(), sys.argv[1:3])
assert subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"], text=True).strip() == "c95b9325913abacca9c86bdebad10a20633cd04e"
assert not subprocess.check_output(["git", "-C", str(dest), "status", "--porcelain"], text=True).strip(), "target must initially be clean"
for f in ["frogdrop.rs", "midg.rs", "tests_midg_k24.rs"]:
    shutil.copyfile(compact / "src/point_add" / f, dest / "src/point_add" / f)
path = dest / "src/point_add/midg.rs"
text = path.read_text()
text = text.replace("precision24", "precision25")
text = text.replace("cp.sz.0 >= 57 && cp.sz.1 <= 256", "cp.sz.0 >= 58 && cp.sz.1 <= 256")
text = text.replace("let top_head = if precision25 { 24 } else { k };", "let top_head = if precision25 { 25 } else { k };")
text = text.replace("if precision25 { reciprocal_r.extend([sx[1], sx[2], sx[3], sx[4], sx[5]]); reciprocal_r.push(ring[n - 1]); }",
                    "if precision25 { reciprocal_r.push(ring[k + 1]); reciprocal_r.extend([sx[1], sx[2], sx[3], sx[4], sx[5]]); reciprocal_r.push(ring[n - 1]); }")
text = text.replace("if precision25 { ring[n - 24..n].to_vec() }", "if precision25 { ring[n - 25..n].to_vec() }")
text = text.replace("assert_eq!(reciprocal_r.len(), 24);", "assert_eq!(reciprocal_r.len(), 25);")
text = text.replace("// N276 has physical K17 and h19. Keep the 24-bit head; the compact\n    // remainder uses ring[0..18], sx[1..5], and ring[275] (24 lanes).\n    // ring[18], the window top, is no longer reciprocal scratch.",
                    "// N276 has physical K17 and h19. The compact representation funds a\n    // 25-bit divisor head in the original 25 remainder lanes: ring[0..19],\n    // SX1..SX5, and ring[275]. Window top ring[18] is never added by V and\n    // returns before a search predicate. QB23 and all quotient owners stay fixed.")
text = text.replace("// The physical window starts at K+1=18, but the reciprocal reads the top 24 ring\n    // lanes. The care rotation must preserve all 24 destination lanes.",
                    "// The physical window starts at K+1=18; the reciprocal now reads the top\n    // 25 ring lanes. The care rotation preserves all 25 destination lanes.")
path.write_text(text)

test = r'''

// Exact compact-packet shot1170/division2/column35 regression. K24 fails this
// arithmetic state in both public and compact sources. This is one HR column
// without payload; it does not claim a complete point-addition record.
#[test]
fn k25_counterexample_col35_exact_euclid_inverse_phase() {
    use super::frogdrop_col::{Fd, ColScr, column_pl};
    let dx = N::from_str_radix("e1a14a46e6340fd02bde43002b9b85d32649195df078b8aa7efe88ce0964f802", 16).unwrap();
    let (mut rs, mut ts) = (vec![super::frogdrop_sched::p(), dx], vec![N::ZERO, N::from(1u64)]);
    while !rs[rs.len()-1].is_zero() {
        let n=rs.len();let q=rs[n-2]/rs[n-1];let rn=rs[n-2]-q*rs[n-1];let tn=ts[n-2]+q*ts[n-1];rs.push(rn);ts.push(tn);
    }
    let j=36;let mut b=builder();let ring=b.alloc_n(276);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();
    let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),693);
    let mut fd=Fd{ring:ring.clone(),q:q.clone(),sy:sy.clone(),sx:sx.clone(),ph,cnt:q[121..].to_vec()};
    let (cols,_,_)=super::pointadd_frogdrop::col_pars(&super::frogdrop_sched::from_text(super::pointadd_frogdrop::SCHED_FROGDROP));
    let cp=&cols[35];assert!(cp.hr&&!cp.ht&&!cp.sw&&!cp.dn);
    let sc=ColScr::carve_col(&pool,&sx,&dirty,24,23,40,cp.sz.1>255);
    let rev:Vec<_>=ring.iter().rev().copied().collect();let mut input=vec![0u64;693];let mut rng=Rng::new(0x20261014_1170);
    for &qid in &dirty {input[qid.0 as usize]=rng.next();}
    for lane in 0..64 {put(&mut input,&ring,lane,rs[j]);put(&mut input,&rev[..ts[j].bit_len()],lane,ts[j]);put(&mut input,&q,lane,ts[j-1]);put(&mut input,&sy,lane,N::from(ts[j].bit_len()as u64));}
    let mut expected=input.clone();for &qid in &ring{expected[qid.0 as usize]=0;}
    for lane in 0..64 {put(&mut expected,&ring,lane,rs[j+1]);put(&mut expected,&rev[..ts[j+1].bit_len()],lane,ts[j+1]);put(&mut expected,&q,lane,ts[j]);put(&mut expected,&sy,lane,N::ZERO);put(&mut expected,&sx,lane,N::from(ts[j+1].bit_len()as u64));}
    b.begin();column_pl(&mut b,&mut fd,cp,&sc,None);let record=b.end();
    let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);
    let got=run(&forward,693,&|words|*words=input.clone());assert_eq!(got.phase,0);assert_eq!(got.q,expected,"exact Euclidean step and every scratch/passenger");
    let back=run(&inverse,693,&|words|*words=got.q.clone());assert_eq!(back.phase,0);assert_eq!(back.q,input);
    eprintln!("K25_COL35_REGRESSION_PASS width=693 shots=64 exact_q=2216631 arithmetic=true dirty_passengers=259 phase=0 inverse=true scope=one_column_no_payload");
}
'''
test_path = dest / "src/point_add/tests_midg_k24.rs"
test_path.write_text(test_path.read_text() + test)
manifest = dict(base_revision="c95b9325913abacca9c86bdebad10a20633cd04e",
                scope="Isolated K25/QB23 precision repair; no full benchmark or Q692 claim",
                nonce_changed=False, source_sha256={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in [dest/"src/point_add/frogdrop.rs", path, test_path]})
print(json.dumps(manifest, indent=2))
