"""Exact same bounded normalization with linear sorted-vector XOR merges."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'recursive-unfold-fast-tool';assert not d.exists()
shutil.copytree(r/'recursive-unfold-tool',d,ignore=shutil.ignore_patterns('target'))
p=d/'src/interned_anf_retained.rs';s=p.read_text();begin=s.index('        // Every stored definition contains strictly older immutable IDs.');end=s.index('        if atoms.len() > atom_cap() {',begin);old=s[begin:end]
s=s[:begin]+'''        atoms=self.unfold_terms_fast(atoms,atom_cap().saturating_mul(4),64);
'''+s[end:]
helper='''    fn unfold_terms_fast(&self,atoms:Vec<u64>,budget:usize,steps:usize)->Vec<u64>{
        let mut flat=atoms;
        let mut pending:std::collections::BTreeSet<u64>=flat.iter().copied().filter(|id|self.large_defs.contains_key(id)).collect();
        for _ in 0..steps {
            let Some(id)=pending.pop_last()else{break;};
            if flat.binary_search(&id).is_err(){continue;}
            let def=&self.large_defs[&id];assert!(def.iter().all(|term|*term<id));assert!(def.windows(2).all(|w|w[0]<w[1]));
            // Symmetric difference after removing id, in exactly the same
            // sorted order as the old ordered-set implementation.
            let mut candidate=Vec::with_capacity(flat.len()+def.len()-1);let(mut i,mut j)=(0,0);
            while i<flat.len()||j<def.len(){
                if i<flat.len()&&flat[i]==id{i+=1;continue;}
                if j==def.len()||(i<flat.len()&&flat[i]<def[j]){candidate.push(flat[i]);i+=1;}
                else if i==flat.len()||def[j]<flat[i]{candidate.push(def[j]);j+=1;}
                else{i+=1;j+=1;}
            }
            if candidate.len()>budget{continue;}
            flat=candidate;
            for &term in def{if flat.binary_search(&term).is_ok()&&self.large_defs.contains_key(&term){pending.insert(term);}}
        }
        flat
    }
    #[cfg(test)]
    fn unfold_terms_reference(&self,mut atoms:Vec<u64>,budget:usize,steps:usize)->Vec<u64>{
'''
reference=old[old.index('        if atoms.iter()'):]
reference=reference.replace('            let budget=atom_cap().saturating_mul(4);\n','').replace('for _ in 0..64','for _ in 0..steps')
helper+=reference+'        atoms\n    }\n'
at=s.index('    fn xor(');s=s[:at]+helper+s[at:]
tests='''
    #[test]
    fn sorted_vector_normalization_matches_ordered_set_oracle(){
        let mut s=Support::new(&[]);let mut rng=0x123456789abcdefu64;
        fn word(r:&mut u64)->u64{*r^=*r<<13;*r^=*r>>7;*r^=*r<<17;*r}
        for _ in 0..32{s.fresh();}
        for _ in 0..100{let mut terms=std::collections::BTreeSet::new();for _ in 0..(word(&mut rng)%32+1){let id=word(&mut rng)%s.next_atom;if !terms.insert(id){terms.remove(&id);}}s.retain_large(false,terms.into_iter().collect());}
        for _ in 0..256{let mut atoms=std::collections::BTreeSet::new();for _ in 0..(word(&mut rng)%24+1){let id=word(&mut rng)%s.next_atom;if !atoms.insert(id){atoms.remove(&id);}}
            for budget in [4,16,64,128,512]{for steps in [0,1,4,64]{let atoms:Vec<_>=atoms.iter().copied().collect();assert_eq!(s.unfold_terms_fast(atoms.clone(),budget,steps),s.unfold_terms_reference(atoms,budget,steps));}}
        }
        s.large_defs.clear();assert_eq!(s.unfold_terms_fast(vec![0,1,2],128,64),vec![0,1,2]);
    }
'''
s=s[:-2]+tests+'}\n';p.write_text(s)
print('Sorted-vector symmetric difference preserves original descending expansion order,64-step cap,4x live-term cap and resulting canonical terms.5120 direct oracle comparisons plus all prior native proofs required.')
