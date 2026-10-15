from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
dest=root/'scratch-tool'
shutil.copytree(root/'analyzer',dest,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
text=(root/'analyzer/src/lazy_cache_retained.rs').read_text()
old='    optimize_impl(ops,split)'
assert text.count(old)==1
text=text.replace(old,'    optimize_impl_with_scratch(ops,split,std::env::var("CACHE_EXTRA_QUBITS").ok().map_or(0,|s|s.parse().unwrap()))')
old='fn optimize_impl(ops:Vec<Op>,split:bool)->Vec<Op> {'
assert text.count(old)==1
text=text.replace(old,'fn optimize_impl(ops:Vec<Op>,split:bool)->Vec<Op> {optimize_impl_with_scratch(ops,split,0)}\nfn optimize_impl_with_scratch(ops:Vec<Op>,split:bool,extra:usize)->Vec<Op> {')
needle='    let nb=ops.iter()'
assert text.count(needle)==1
text=text.replace(needle,'    let original_nq=nq;let nq=nq+extra;\n'+needle)
needle='w.donors=symbolic.cache_zeros().into_iter().filter(|q|snap[&i][*q]>=w.end).collect();wi+=1;'
assert text.count(needle)==1
text=text.replace(needle,'w.donors=symbolic.cache_zeros().into_iter().filter(|q|snap[&i][*q]>=w.end).chain(original_nq..nq).collect();wi+=1;')
text+='''
#[cfg(test)]
mod scratch_tests {
    use super::*;
    use crate::circuit::RegisterId;
    use quantum_ecc::sim::Simulator;
    struct Word(u64);
    impl sha3::digest::XofReader for Word {fn read(&mut self,out:&mut [u8]){out.copy_from_slice(&self.0.to_le_bytes());}}
    #[test]
    fn fresh_scratch_exhaustive_dirty_input_guards_and_phase() {
        let mut p=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=RegisterId(0);p.push(r);
        for q in 0..5 {let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);p.push(o);}
        for b in 0..2 {let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.c_target=BitId(b);p.push(o);}
        p.extend([gate(K::CCX,Some(0),Some(1),Some(2),None,Some(0)),gate(K::CCX,Some(0),Some(1),Some(3),None,Some(1)),gate(K::X,None,None,Some(4),None,None),gate(K::X,None,None,Some(4),None,None)]);
        assert_eq!(optimize_impl(p.clone(),true),p);
        let q=optimize_impl_with_scratch(p.clone(),true,1);
        assert!(q.iter().any(|o|o.q_target==QubitId(5)));
        let mut total_saved=0;
        for word in [0,u64::MAX,0xa5a5a5a5a5a5a5a5,0x0123456789abcdef] {for batch in 0..2 {
            let(mut xa,mut xb)=(Word(word),Word(word));
            let mut a=Simulator::new(5,8,&mut xa);let mut b=Simulator::new(6,8,&mut xb);
            for k in 0..7 {let v=(0..64).fold(0u64,|v,l|v|(((((batch*64+l)>>k)&1)as u64)<<l));if k<5 {a.qubits[k]=v;}else{a.bits[k-5]=v;}}
            a.phase=0x55aa55aa55aa55aa;b.qubits[..5].copy_from_slice(&a.qubits);b.bits=a.bits.clone();b.phase=a.phase;
            a.apply_iter(p.iter());b.apply_iter(q.iter());assert_eq!(a.qubits,b.qubits[..5]);assert_eq!(a.phase,b.phase);assert_eq!(a.bits,b.bits);assert_eq!(b.qubits[5],0);assert!(b.stats.toffoli_gates<=a.stats.toffoli_gates);total_saved+=a.stats.toffoli_gates-b.stats.toffoli_gates;
        }}assert!(total_saved>0);
    }
}
'''
(dest/'src/lazy_cache_retained.rs').write_text(text)
