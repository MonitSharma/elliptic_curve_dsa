"""Preserve inconclusive global proof; add an exact arbitrary-cut local proof."""
import hashlib, json, shutil
from pathlib import Path
r = Path(__file__).resolve().parent
old = r / 'parent4-transfer-v2'
out = r / 'parent4-transfer-local'
assert (r / 'parent4-transfer-v3.exit').read_text().strip() == '101'
assert 'unequal product at 14247262' in (old / 'verify.log').read_text()
out.mkdir(exist_ok=False)
for name in ['Cargo.toml', 'Cargo.lock', 'io.rs', 'leases.json']:
    shutil.copyfile(old / name, out / name)
discovery = (r / 'discover.rs').read_text()
local = discovery[discovery.index('fn local_proof('):discovery.index('fn tri_and(')]
source = (old / 'verify.rs').read_text()
needle = 'assert_eq!(product.as_ref().unwrap(),&expected[&(s[0]as usize)],"unequal product at {i}");'
assert source.count(needle) == 1
source = source.replace(needle, 'assert!(product.as_ref().unwrap()==&expected[&(s[0]as usize)] || local_proof(ops,s[0]as usize,i,nq,nb),"neither global nor arbitrary-cut local proof established product equality at {i}");')
source += '\n' + local + r'''
#[cfg(test)] mod proof_tests {
 use super::*;
 #[test] fn local_identity_and_nonidentity(){
  let n=u64::MAX;
  let good=vec![make(K::CCX,0,1,2,n,n),make(K::CX,n,0,1,n,n),make(K::X,n,n,1,n,n),make(K::CCX,0,1,3,n,n)];
  assert!(local_proof(&good,0,3,4,0));
  let mut bad=good;bad.remove(2);assert!(!local_proof(&bad,0,2,4,0));
 }
 #[test] fn unknown_conditional_change_is_not_skipped(){
  let n=u64::MAX;
  let ops=vec![make(K::CCX,0,1,2,n,n),make(K::X,n,n,1,n,0),make(K::CCX,0,1,3,n,n)];
  assert!(!local_proof(&ops,0,2,4,1));
 }
}
'''
(out / 'verify.rs').write_text(source)
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
(out / 'PROOF-SOURCE.json').write_text(json.dumps(manifest, indent=2) + '\n')
(out / 'RETRY.json').write_text(json.dumps({'reason': 'Global truncation did not establish the second product equality.',
    'method': 'Existing collision-free local proof starts with arbitrary independent wire/bit values and arbitrary measurements; acceptance requires exact full-expression equality. Global proof still establishes clean, untouched donors and unconditional endpoints.',
    'circuit_changed': False, 'statistical_gate_rerun': False}, indent=2) + '\n')
