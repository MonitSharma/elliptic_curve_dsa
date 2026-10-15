impl Support {
    // Exact XOR identities in an over-approximation of reachable values.
    // Every atom is immutable; forgetting correlations only loses identities.
    pub(crate) fn loan_relation(&self, top:usize, nt:&[usize], nw:&[usize], end:usize)->Option<(usize,Vec<usize>,bool)> {
        use std::collections::{BTreeSet,HashMap};
        let mut basis:HashMap<u64,(BTreeSet<u64>,BTreeSet<usize>,bool)>=HashMap::new();
        let mut order:Vec<usize>=(0..top).filter(|q|nw[*q]>end).collect();
        // Keep wires read during the interval as basis; prefer unused wires as loans.
        order.sort_by_key(|q|(nt[*q]>end,self.qubits[*q].atoms.len()));
        for q in order {
            let mut atoms:BTreeSet<u64>=self.qubits[q].atoms.iter().copied().collect();
            let mut wires=BTreeSet::from([q]);let mut constant=self.qubits[q].constant;
            while let Some(&pivot)=atoms.last(){
                if let Some((a,w,c))=basis.get(&pivot) {
                    atoms=atoms.symmetric_difference(a).copied().collect();
                    wires=wires.symmetric_difference(w).copied().collect();constant^=c;
                }else{basis.insert(pivot,(atoms.clone(),wires.clone(),constant));break;}
            }
            if atoms.is_empty()&&nt[q]>end {
                assert!(wires.remove(&q));
                return Some((q,wires.into_iter().collect(),constant));
            }
        }
        None
    }
}
