
    pub(crate) fn research_prime_clean_pool(&mut self, cap:usize) {
        let active=self.active_qubits();assert!(active as usize<=cap);
        let before=self.op_count();let idle=self.alloc_qubits(cap-active as usize);
        for q in idle.into_iter().rev(){self.release_clean(q);}
        assert_eq!(self.active_qubits(),active);assert_eq!(self.op_count(),before,"Priming must emit no operations");
    }
