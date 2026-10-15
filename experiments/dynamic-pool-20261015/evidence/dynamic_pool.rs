// Dynamic checkpoints retain the fresh-ID boundary as well as the free lists.
pub(crate) type Y42Checkpoint = ((Vec<u32>, Vec<u32>, u32), u32, u32);
impl Builder {
    pub(crate) fn y42_dynamic_checkpoint(&self) -> Y42Checkpoint {
        (self.y42_alloc_state(),self.next_qubit,self.active_qubits)
    }
    pub(crate) fn y42_dynamic_restore(&mut self, checkpoint:&Y42Checkpoint) {
        let (before,next_q,active)=checkpoint;
        assert!(self.next_qubit>=*next_q,"dynamic allocator: quantum counter regressed");
        assert_eq!(self.active_qubits,*active,"dynamic allocator: live count changed");
        assert!(before.0.iter().all(|&q|q<*next_q),"dynamic allocator: invalid old free ID");
        let mut old=before.0.clone();old.sort_unstable();
        assert!(old.windows(2).all(|w|w[0]!=w[1]),"dynamic allocator: duplicate old free ID");
        // Old free wires keep their stack priority. Fresh returned wires are
        // below them, in the same increasing-ID order as lazy allocation.
        let mut expected:Vec<u32>=(*next_q..self.next_qubit).rev().collect();
        expected.extend_from_slice(&before.0);
        let augmented=(expected.clone(),before.1.clone(),before.2);
        // Reuse every existing wire-set and classical-bit ownership assertion.
        // Missing fresh wires, extra live-wire frees and duplicates all fail.
        self.y42_alloc_set(&augmented,&expected,before.1.len(),&[],before.2);
        if self.next_qubit>*next_q {eprintln!("Y42_FRESH_RETURNED before_next={} after_next={} fresh={} active={}",next_q,self.next_qubit,self.next_qubit-next_q,active);}
    }
}
#[cfg(test)]
mod dynamic_pool_tests {
    use super::*;
    #[test]
    fn returned_fresh_wires_keep_old_order_and_lazy_id_order(){
        let mut c=Builder::new();let live=c.alloc_qubit();let old=c.alloc_qubits(3);
        c.release_clean(old[1]);c.release_clean(old[0]);c.release_clean(old[2]);
        let cp=c.y42_dynamic_checkpoint();let before_ops=c.ops.len();
        let used=c.alloc_qubits(6);for &q in &used{c.release_clean(q);}
        let bit=c.alloc_bit();c.free_bit(bit);
        c.y42_dynamic_restore(&cp);assert_eq!(c.ops.len(),before_ops);
        let actual:Vec<_>=c.alloc_qubits(6).into_iter().map(|q|q.0).collect();
        assert_eq!(actual,vec![old[2].0,old[0].0,old[1].0,4,5,6]);assert_eq!(live.0,0);
    }
    #[test]
    fn no_fresh_wires_matches_original_restore(){
        let mut c=Builder::new();let q=c.alloc_qubits(8);for &v in &q{c.release_clean(v);}
        let cp=c.y42_dynamic_checkpoint();let borrowed=c.alloc_qubits(5);for &v in &borrowed{c.release_clean(v);}
        c.y42_dynamic_restore(&cp);assert_eq!(c.y42_alloc_state(),cp.0);assert_eq!(c.next_qubit,cp.1);
    }
    #[test]
    #[should_panic(expected="live count changed")]
    fn fresh_live_wire_is_rejected(){let mut c=Builder::new();let cp=c.y42_dynamic_checkpoint();let _q=c.alloc_qubit();c.y42_dynamic_restore(&cp);}
    #[test]
    #[should_panic(expected="payload op changed the set of free wires")]
    fn balanced_leak_and_illegal_live_free_is_rejected(){
        let mut c=Builder::new();let live=c.alloc_qubit();let spare=c.alloc_qubit();c.release_clean(spare);let cp=c.y42_dynamic_checkpoint();let _leak=c.alloc_qubit();c.release_clean(live);c.y42_dynamic_restore(&cp);
    }
    #[test]
    #[should_panic(expected="payload op changed the set of free wires")]
    fn duplicate_return_is_rejected_even_with_balanced_count(){
        let mut c=Builder::new();let q=c.alloc_qubits(2);for &v in &q{c.release_clean(v);}let cp=c.y42_dynamic_checkpoint();c.free_qubits.push(q[0].0 as u32);c.y42_dynamic_restore(&cp);
    }
    #[test]
    #[should_panic(expected="payload op kept a classical bit")]
    fn fresh_classical_leak_is_rejected(){let mut c=Builder::new();let cp=c.y42_dynamic_checkpoint();let _b=c.alloc_bit();c.y42_dynamic_restore(&cp);}
}
