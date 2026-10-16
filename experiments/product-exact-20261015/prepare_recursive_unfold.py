"""Bounded recursive exact XOR-definition normalization, separate experiment."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'recursive-unfold-tool';assert not d.exists()
shutil.copytree(r/'unfold-tool',d,ignore=shutil.ignore_patterns('target'))
for name in ['lazy_cache.rs','lazy_cache_anf.rs','lazy_cache_retained.rs']:
    shutil.copy2(r/'flags-four-tool/src'/name,d/'src'/name)
p=d/'src/interned_anf_retained.rs';s=p.read_text()
begin=s.index('        // Expand only a bounded small XOR');end=s.index('        if atoms.len() > atom_cap() {',begin)
s=s[:begin]+'''        // Every stored definition contains strictly older immutable IDs.
        // Descending expansion terminates; explicit step/live-term budgets
        // make this a bounded normalization. Declining expansion loses only
        // an equality proof, never changes a function or recycles an ID.
        if atoms.iter().any(|id|self.large_defs.contains_key(id)) {
            let budget=atom_cap().saturating_mul(4);
            let mut flat:std::collections::BTreeSet<u64>=atoms.iter().copied().collect();
            let mut pending:std::collections::BTreeSet<u64>=flat.iter().copied().filter(|id|self.large_defs.contains_key(id)).collect();
            for _ in 0..64 {
                let Some(id)=pending.pop_last() else{break;};
                if !flat.contains(&id){continue;}
                let def=&self.large_defs[&id];assert!(def.iter().all(|term|*term<id));
                let mut candidate=flat.clone();assert!(candidate.remove(&id));
                for &term in def {if !candidate.insert(term){candidate.remove(&term);}}
                if candidate.len()>budget{continue;}
                flat=candidate;
                for &term in def {if flat.contains(&term)&&self.large_defs.contains_key(&term){pending.insert(term);}}
            }
            atoms=flat.into_iter().collect();
        }
'''+s[end:]
tests='''
    #[test]
    fn nested_immutable_xor_definitions_cancel_recursively(){
        let mut s=Support::new(&[]);let mut base=vec![];
        for _ in 0..atom_cap()+3 {base.push(s.fresh().atoms[0]);}
        let a=s.retain_large(false,base[..atom_cap()+1].to_vec());
        let b=s.retain_large(false,vec![base[atom_cap()+1],a.atoms[0]]);
        let c=s.retain_large(true,vec![base[atom_cap()+2],b.atoms[0]]);
        let x=s.xor(&c,&a);assert!(x.constant);assert_eq!(x.atoms,base[atom_cap()+1..].to_vec());
        let z=s.xor(&x,&c);let done=s.xor(&z,&a);assert!(done.is_zero());
    }
'''
s=s[:-2]+tests+'}\n';p.write_text(s)
# Offer scratch only where explicitly requested; compact flags remain per donor.
p=d/'src/lazy_cache_retained.rs';s=p.read_text()
s=s.replace('    optimize_impl(ops,split)','    optimize_impl_with_scratch(ops,split,std::env::var("CACHE_EXTRA_QUBITS").ok().map_or(0,|s|s.parse().unwrap()))',1)
needle='fn optimize_impl(ops:Vec<Op>,split:bool)->Vec<Op> {';assert s.count(needle)==1
s=s.replace(needle,needle+'optimize_impl_with_scratch(ops,split,0)}\nfn optimize_impl_with_scratch(ops:Vec<Op>,split:bool,extra:usize)->Vec<Op> {')
s=s.replace('    let nb=ops.iter()','    let original_nq=nq;let nq=nq+extra;\n    let nb=ops.iter()',1)
needle='w.donors=symbolic.cache_zeros().into_iter().filter(|q|snap[&i][*q]>=w.end).collect();wi+=1;';assert s.count(needle)==1
s=s.replace(needle,'w.donors=symbolic.cache_zeros().into_iter().filter(|q|snap[&i][*q]>=w.end).chain(original_nq..nq).collect();wi+=1;')
scratch=(r/'scratch-tool/src/lazy_cache_retained.rs').read_text();s+=scratch[scratch.index('#[cfg(test)]\nmod scratch_tests'):];p.write_text(s)
print('Exact immutable recursive XOR unfolding:64 expansions,4xatom-cap live term budget, descending IDs; compact per-donor flags, optional declared fresh quantum scratch.')
