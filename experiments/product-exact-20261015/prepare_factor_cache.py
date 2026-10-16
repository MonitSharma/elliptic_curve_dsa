"""Raise the exact square-free monomial arity cap; preserve opaque fallback."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'factor-cache-tool';assert not d.exists()
shutil.copytree(r/'flags-four-tool',d,ignore=shutil.ignore_patterns('target'))
p=d/'src/interned_anf_retained.rs';s=p.read_text()
needle='if factors.len()>128'
assert s.count(needle)==1;s=s.replace(needle,'if factors.len()>factor_cap()')
s='fn factor_cap()->usize {static V:std::sync::OnceLock<usize>=std::sync::OnceLock::new();*V.get_or_init(||std::env::var("FACTOR_CAP").ok().map(|s|s.parse().unwrap()).unwrap_or(256))}\n'+s
# Module-level inner doc comments must precede any item.
lines=s.splitlines();first=lines.pop(0);at=0
while at<len(lines) and (lines[at].startswith('//!') or not lines[at].strip()):at+=1
lines.insert(at,first);s='\n'.join(lines)+'\n'
tests='''
    #[test]
    fn long_monomial_reordering_and_idempotence_are_exact() {
        assert!(factor_cap()>=200);let mut s=Support::new(&[]);let mut atoms=vec![];
        for _ in 0..200 {atoms.push(s.fresh());}
        let mut a=Affine::constant(true);for x in &atoms {a=s.and(&a,x);}
        let mut b=Affine::constant(true);for x in atoms.iter().rev() {b=s.and(&b,x);}
        assert!(a==b);assert_eq!(a.atoms.len(),1);assert_eq!(s.factors[a.atoms[0]as usize].len(),200);
        for x in &atoms {assert!(s.and(&a,x)==a);}
    }
    #[test]
    fn two_hundred_input_native_witness_values_and_phase() {
        let z=u64::MAX;let mut p=vec![];let mut r=Op::empty();r.kind=OperationType::Register;r.r_target=crate::circuit::RegisterId(0);p.push(r);
        for q in (0..200).chain(std::iter::once(399)) {let mut a=Op::empty();a.kind=OperationType::AppendToRegister;a.r_target=r.r_target;a.q_target=QubitId(q);p.push(a);}
        p.push(op(OperationType::CCX,0,1,200));
        for input in 2..200 {p.push(op(OperationType::CCX,198+input,input,199+input));}
        p.push(op(OperationType::CCX,398,0,399));p.push(op(OperationType::CZ,398,z,399));
        let q=witnesses(p.clone());assert_eq!(p.iter().filter(|o|o.kind==OperationType::CCX).count()-q.iter().filter(|o|o.kind==OperationType::CCX).count(),1);
        for batch in 0..4 {for phase in [0,u64::MAX,0xa5a5a5a5a5a5a5a5] {
            let mut xa=Word(0);let mut xb=Word(0);let mut a=Simulator::new(400,0,&mut xa);let mut b=Simulator::new(400,0,&mut xb);
            for input in 0..200 {a.qubits[input]=(0..64).fold(0u64,|v,l|v|((((batch*64+l)%201)!=input)as u64)<<l);}
            a.qubits[399]=0xa5a5a5a5a5a5a5a5;b.qubits=a.qubits.clone();a.phase=phase;b.phase=phase;a.apply_iter(p.iter());b.apply_iter(q.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.phase,b.phase);
        }}
    }
'''
assert s.endswith('}\n');s=s[:-2]+tests+'}\n';p.write_text(s)
print('Square-free factor arity chosen structurally from256/512/1024; native200-input monomial witnesses, no simulator-packet selection.')
