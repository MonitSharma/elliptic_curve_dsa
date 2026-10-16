"""Separate zero and product kernels so bounded proof caches cannot interfere."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate-v2-tool';assert not d.exists()
shutil.copytree(r/'cache-certificate-tool',d,ignore=shutil.ignore_patterns('target'))
p=d/'src/cache_certificate.rs';s=p.read_text()
needle='    let mut state=Symbolic::new(left,mode);let mut product=HashMap::new();'
assert s.count(needle)==1
s=s.replace(needle,'''    // Step-only symbolic pass proves zeros independently of product-query
    // allocations. Bounded caches may forget identities in either pass; IDs
    // are local to a pass and are never compared across the two proofs.
    {
        let mut zero=Symbolic::new(left,mode);
        for i in 0..=left.len(){
            if let Some(js)=starts.get(&i){let zeros:BTreeSet<_>=zero.zeros().into_iter().collect();for &j in js{
                assert!(zeros.contains(&plans[j].donor),"donor zero unproved: lease={j} start={i} donor={}",plans[j].donor);
            }}
            if i<left.len(){zero.step(&left[i]);}
        }
    }
'''+needle)
needle='''        if let Some(js)=starts.get(&i){let zeros:BTreeSet<_>=state.zeros().into_iter().collect();for &j in js{
            let p=&plans[j];assert!(zeros.contains(&p.donor),"donor not universally zero at lease start");assert!(live.insert(p.donor,j).is_none(),"quantum donor leases overlap");'''
assert s.count(needle)==1
s=s.replace(needle,'''        if let Some(js)=starts.get(&i){for &j in js{
            let p=&plans[j];assert!(live.insert(p.donor,j).is_none(),"quantum donor leases overlap");''')
s=s.replace('no_simulated_inputs=true",plans.len()','no_simulated_inputs=true independent_zero_and_product_passes=true",plans.len()');p.write_text(s)
print('All original obligations retained; separate conservative step-only zero proof and query-aware product proof, with no cross-pass ID comparison.')
