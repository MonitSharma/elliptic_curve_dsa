"""Preserve exact boundary relations when invoking the bounded local proof.

Boundary expressions are proven by the global interpreter. Every nonconstant
atom may be treated as independent in the local check; this weakens knowledge
and cannot establish an invalid identity. New atoms start above every existing
ID. No unknown flag is assigned a guessed constant.
"""
import hashlib, json, shutil
from pathlib import Path
r = Path(__file__).resolve().parent
old = r / 'parent4-transfer-local'
out = r / 'parent4-transfer-seeded'
assert (r / 'parent4-transfer-local.exit').read_text().strip() == '101'
out.mkdir(exist_ok=False)
for name in ['Cargo.toml', 'Cargo.lock', 'io.rs', 'leases.json']:
    shutil.copyfile(old / name, out / name)
source = (old / 'verify.rs').read_text()
source = source.replace('let mut expected:HashMap<usize,E>=HashMap::new();', 'let mut boundaries:HashMap<usize,(Vec<E>,Vec<E>,E,Vec<E>,u32)>=HashMap::new();let mut expected:HashMap<usize,E>=HashMap::new();')
source = source.replace('active.insert(s[2],i);expected.insert(i,product.clone().unwrap());', 'active.insert(s[2],i);expected.insert(i,product.clone().unwrap());boundaries.insert(i,(q.clone(),c.clone(),base.clone(),stack.clone(),alg.next));')
source = source.replace('|| local_proof(ops,s[0]as usize,i,nq,nb)', '|| seeded_proof(ops,s[0]as usize,i,&boundaries[&(s[0]as usize)])')
start = source.index('fn local_proof(')
end = source.index('\n#[cfg(test)]', start)
local = source[start:end]
local = local.replace('fn local_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool{', 'fn seeded_proof(ops:&[Op],first:usize,last:usize,boundary:&(Vec<E>,Vec<E>,E,Vec<E>,u32))->bool{')
local = local.replace('Algebra{next:1,', 'Algebra{next:boundary.4,')
local = local.replace('let mut q:Vec<E>=(0..nq).map(|_|alg.fresh()).collect();let mut c:Vec<E>=(0..nb).map(|_|alg.fresh()).collect();', 'let mut q=boundary.0.clone();let mut c=boundary.1.clone();')
local = local.replace('let mut base=vec![0];let mut stack=vec![];', 'let mut base=boundary.2.clone();let mut stack=boundary.3.clone();')
local = local.replace('stack.is_empty()&&base==vec![0]&&', '')
assert 'nq' not in local and 'nb' not in local
source += '\n' + local + r'''
#[cfg(test)]mod boundary_tests{
 use super::*;
 #[test]fn known_flag_is_used_but_unknown_flag_is_not_assumed(){
  let n=u64::MAX;
  let ops=vec![make(K::CCX,0,1,2,n,n),make(K::X,n,n,0,n,0),make(K::CCX,0,1,3,n,n)];
  let q=vec![vec![1],vec![2],vec![3],vec![4]];
  assert!(seeded_proof(&ops,0,2,&(q.clone(),vec![vec![]],vec![0],vec![],6)));
  assert!(!seeded_proof(&ops,0,2,&(q,vec![vec![5]],vec![0],vec![],6)));
 }
}
'''
(out / 'verify.rs').write_text(source)
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
(out / 'PROOF-SOURCE.json').write_text(json.dumps(manifest, indent=2) + '\n')
(out / 'RETRY.json').write_text(json.dumps({'reason': 'Independent arbitrary-cut proof loses globally proven boundary flags and relations.',
    'method': __doc__, 'circuit_changed': False, 'statistical_gate_rerun': False}, indent=2) + '\n')
