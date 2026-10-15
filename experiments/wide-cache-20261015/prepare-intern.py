"""Exact immutable interning of over-cap XORs; cache eviction loses only proofs."""
from pathlib import Path
root=Path(__file__).resolve().parent
dest=root/'intern-tool'
(dest/'src').mkdir(parents=True,exist_ok=True)
old=root.parent/'cache-retention-20261015/analyzer'
for name in ['main.rs','lazy_cache.rs','interned_witness.rs']:
 (dest/'src'/name).write_bytes((old/'src'/name).read_bytes())
for name in ['Cargo.toml','Cargo.lock']:
 (dest/name).write_bytes((old/name).read_bytes())
p=dest/'src/interned_witness.rs'
s=p.read_text()
needle='    products: std::collections::HashMap<(Vec<u64>,Vec<u64>),u64>,'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n    oversized: std::collections::HashMap<Vec<u64>,u64>,')
needle='            products: std::collections::HashMap::new(),'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n            oversized: std::collections::HashMap::new(),')
needle='''            // This fresh atom represents the entire XOR, including its
            // constant. It must not be mistaken for zero or an older atom.
            self.fresh()'''
assert s.count(needle)==1
s=s.replace(needle,'''            // The sorted immutable atomset denotes an exact Boolean XOR.
            // Equal keys denote equal functions; no hash-only equality is used.
            // Keep the constant outside so complements stay complements.
            let id = if let Some(&id)=self.oversized.get(&atoms) {id} else {
                // Eviction never recycles IDs: live old atoms retain their meaning.
                if self.oversized.len()>=200_000 {self.oversized.clear();}
                let id=self.fresh().atoms[0];self.oversized.insert(atoms,id);id
            };
            Affine {constant:a.constant^b.constant,atoms:vec![id]}''')
s+='''
#[cfg(test)]
mod intern_tests {
 use super::*;
 fn support()->Support {Support{qubits:vec![],bits:vec![],base_condition:Affine::constant(true),condition_stack:vec![],next_atom:0,products:std::collections::HashMap::new(),oversized:std::collections::HashMap::new()}}
 #[test] fn oversized_repeats_and_complements_are_exact(){
  let mut s=support();let cap=atom_cap();
  let a=Affine{constant:false,atoms:(0..cap).map(|_|s.fresh().atoms[0]).collect()};
  let b=s.fresh();let x=s.xor(&a,&b);let y=s.xor(&a,&b);
  assert!(x==y);assert!(x.atoms.len()==1);assert!(!x.is_zero());
  let z=s.xor(&a.complement(),&b);assert!(x.complements(&z));
  let cancelled=s.xor(&x,&y);assert!(cancelled.is_zero());
  let differing=s.fresh();let other=s.xor(&a,&differing);assert!(x!=other);
 }
 #[test] fn eviction_does_not_recycle_an_atom(){
  let mut s=support();let cap=atom_cap();
  let a=Affine{constant:false,atoms:(0..cap).map(|_|s.fresh().atoms[0]).collect()};
  let b=s.fresh();let x=s.xor(&a,&b);s.oversized.clear();
  let y=s.xor(&a,&b);assert!(x!=y);assert!(!s.xor(&x,&y).is_zero());
 }
}
'''
p.write_text(s)
