#[cfg(test)]
mod tests {
    use super::*;
    use crate::circuit::RegisterId;
    use quantum_ecc::sim::Simulator;
    struct Word(u64);
    impl sha3::digest::XofReader for Word {fn read(&mut self,out:&mut [u8]){assert_eq!(out.len(),8);out.copy_from_slice(&self.0.to_le_bytes());}}
    fn program()->Vec<Op>{
        let mut p=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=RegisterId(0);p.push(r);
        for q in 0..5 {let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);p.push(o);}
        for b in 0..4 {let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.c_target=BitId(b);p.push(o);}
        p.extend([
            push(0),gate(K::BitInvert,None,None,None,Some(0),None),
            gate(K::CCX,Some(0),Some(1),Some(4),None,Some(1)),pop(),
            gate(K::CCX,Some(2),Some(3),Some(4),None,Some(2)),
            gate(K::R,None,None,Some(5),None,None),
            gate(K::X,None,None,Some(0),None,None),gate(K::CZ,Some(3),None,Some(4),None,None),
            gate(K::X,None,None,Some(0),None,None),
            push(3),gate(K::CCX,Some(0),Some(1),Some(2),None,Some(1)),pop(),
            gate(K::CCX,Some(0),Some(1),Some(4),None,None),
            gate(K::R,None,None,Some(7),None,None),
        ]);
        p
    }
    fn run_case(p:&[Op],q:&[Op],batch:usize,word:u64)->(Vec<u64>,Vec<u64>,Vec<u64>,Vec<u64>,u64,u64,u64,u64){
        let mut xa=Word(word);let mut xb=Word(word);
        let mut a=Simulator::new(8,64,&mut xa);let mut b=Simulator::new(8,64,&mut xb);
        for bit in 0..9 {let v=(0..64).fold(0u64,|v,l|v|((((batch*64+l)>>bit)&1) as u64)<<l);if bit<5 {a.qubits[bit]=v;}else{a.bits[bit-5]=v;}}
        for bit in 4..64{a.bits[bit]=0xa5a5a5a5a5a5a5a5;}
        a.phase=0x55aa55aa55aa55aa;b.qubits=a.qubits.clone();b.bits=a.bits.clone();b.phase=a.phase;
        a.apply_iter(p.iter());b.apply_iter(q.iter());
        (a.qubits,b.qubits,a.bits,b.bits,a.phase,b.phase,a.stats.toffoli_gates,b.stats.toffoli_gates)
    }
    #[test]
    fn lazy_cache_native_dirty_abi_guards_and_phase(){
        let p=program();let q=optimize(p.clone());assert!(q.len()>p.len());let mut saved=0;
        for word in [0,u64::MAX,0xa5a5a5a5a5a5a5a5,0x5a5a5a5a5a5a5a5,0x5555aaaaffff0000,0x0123456789abcdef] {
            for batch in 0..8 {
                let (aq,bq,ab,bb,ap,bp,ac,bc)=run_case(&p,&q,batch,word);
                assert_eq!(aq,bq);assert_eq!(&ab[..4],&bb[..4]);assert_eq!(ap,bp);assert!(bc<=ac);saved+=ac-bc;
                // Exactly the three fresh flags for the one selected lease are clean.
                for bit in 4..7 {assert_eq!(bb[bit],0);}
                assert_eq!(&ab[7..],&bb[7..]);
            }
        }
        assert!(saved>0);println!("LAZY_NATIVE cases=3072 saved={saved}");
    }
    #[test]
    fn lazy_cache_phase_fault_is_detected(){
        let p=program();let mut q=optimize(p.clone());let at=q.iter().position(|o|o.kind==K::CZ&&o.c_condition.0>=4&&o.c_condition!=NO_BIT).unwrap();q.remove(at);
        let mut detected=false;for batch in 0..8 {let (_,_,_,_,a,b,_,_)=run_case(&p,&q,batch,u64::MAX);detected|=a!=b;}assert!(detected);
    }
    #[test]
    fn lazy_cache_overlapping_leases_all_outcome_patterns(){
        let mut p=program()[..10].to_vec();
        p.extend([
            gate(K::CCX,Some(0),Some(1),Some(4),None,Some(0)),
            gate(K::CCX,Some(2),Some(3),Some(4),None,Some(1)),
            gate(K::R,None,None,Some(5),None,None),
            gate(K::CCX,Some(0),Some(1),Some(4),None,Some(2)),
            gate(K::CCX,Some(2),Some(3),Some(4),None,Some(3)),
            gate(K::R,None,None,Some(7),None,None),
        ]);
        let q=optimize(p.clone());assert_eq!(q,optimize(p.clone()));
        let mr=q.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).count();assert_eq!(mr,3);
        struct Events{pattern:usize,at:usize}
        impl sha3::digest::XofReader for Events{fn read(&mut self,out:&mut[u8]){assert_eq!(out.len(),8);let word=if self.pattern>>self.at&1==0{0u64}else{u64::MAX};self.at+=1;out.copy_from_slice(&word.to_le_bytes());}}
        for pattern in 0..1<<mr {for batch in 0..8 {
            let mut xa=Word(0);let mut xb=Events{pattern,at:0};
            let mut a=Simulator::new(8,64,&mut xa);let mut b=Simulator::new(8,64,&mut xb);
            for bit in 0..9{let v=(0..64).fold(0u64,|v,l|v|((((batch*64+l)>>bit)&1)as u64)<<l);if bit<5{a.qubits[bit]=v;}else{a.bits[bit-5]=v;}}
            for bit in 4..64{a.bits[bit]=0xa5a5a5a5a5a5a5a5;}
            a.phase=0x55aa55aa55aa55aa;b.qubits=a.qubits.clone();b.bits=a.bits.clone();b.phase=a.phase;
            a.apply_iter(p.iter());b.apply_iter(q.iter());
            assert_eq!(a.qubits,b.qubits);assert_eq!(&a.bits[..4],&b.bits[..4]);assert_eq!(a.phase,b.phase);assert!(b.stats.toffoli_gates<=a.stats.toffoli_gates);
            for bit in 4..10{assert_eq!(b.bits[bit],0);}assert_eq!(&a.bits[10..],&b.bits[10..]);
        }}
        println!("LAZY_OVERLAP_NATIVE cases=4096 independent_event_patterns=8 deterministic=true");
    }
}
