"""Separate exact factored Boolean normal form, without ANF distribution."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'factored-cache-tool';assert not d.exists()
shutil.copytree(r/'factor-witness-tool',d,ignore=shutil.ignore_patterns('target'))
p=d/'src/interned_anf_retained.rs';s=p.read_text()
s=s.replace('    products: std::collections::HashMap<(Vec<u64>,Vec<u64>),u64>,','    complements: std::collections::HashMap<u64,u64>,')
s=s.replace('            products: std::collections::HashMap::new(),','            complements: std::collections::HashMap::new(),')
begin=s.index('    fn and(&mut self,');end=s.index('    fn ccx_rewrite',begin)
s=s[:begin]+'''    // A node is an immutable complete Boolean function. XOR nodes preserve
    // their exact term set; AND nodes flatten only exact AND children. No ANF
    // distribution or assumption of independence is used.
    fn root_id(&mut self,a:&Affine)->u64 {
        assert!(!a.atoms.is_empty());
        let id=if a.atoms.len()==1{a.atoms[0]}else{self.retain_large(false,a.atoms.clone()).atoms[0]};
        if !a.constant{return id;}
        if let Some(&neg)=self.complements.get(&id){return neg;}
        let neg=self.fresh().atoms[0];self.complements.insert(id,neg);self.complements.insert(neg,id);neg
    }

    fn and(&mut self,a:&Affine,b:&Affine)->Affine {
        if a.is_zero()||b.is_zero()||a.complements(b){return Affine::constant(false);}
        if a.is_one(){return b.clone();}
        if b.is_one()||a==b{return a.clone();}
        let x=self.root_id(a);let y=self.root_id(b);
        let mut factors=self.factors[x as usize].clone();
        factors.extend_from_slice(&self.factors[y as usize]);factors.sort_unstable();factors.dedup();
        // If an AND contains !F and every factor of F, it is zero. This also
        // proves A*B*!(A*B)=0 when the positive AND was flattened away.
        for &id in &factors {
            if let Some(&other)=self.complements.get(&id){
                if self.factors[other as usize].iter().all(|f|factors.binary_search(f).is_ok()){
                    return Affine::constant(false);
                }
            }
        }
        if factors.len()>factor_cap(){return self.fresh();}
        let id=if factors.len()==1{factors[0]}else if let Some(&id)=self.monomial_products.get(&factors){id}else{
            if self.monomial_products.len()>=product_cap(){self.monomial_products.clear();}
            let id=self.fresh().atoms[0];self.factors[id as usize]=factors.clone();self.monomial_products.insert(factors,id);id
        };
        Affine{constant:false,atoms:vec![id]}
    }

'''+s[end:]
s=s.replace('                let toggle = self.and(&condition, &product);','                let toggle = self.and(&condition, &product);\n                if product.is_zero(){rewrite=Rewrite::Drop;}')
# The ANF-only distributivity gain is deliberately absent in this alternative.
old='assert_eq!(p.iter().filter(|o|o.kind==OperationType::CCX).count()-q.iter().filter(|o|o.kind==OperationType::CCX).count(),1);'
assert s.count(old)==2
at=s.index(old);s=s[:at]+s[at:].replace(old,'assert!(q.iter().filter(|o|o.kind==OperationType::CCX).count()<=p.iter().filter(|o|o.kind==OperationType::CCX).count());',1)
tests='''
    #[test]
    fn polynomial_factor_reassociation_and_complement_absorption(){
        let mut s=Support::new(&[]);let mut forms=vec![];
        for group in 0..3 {let mut a=Affine::constant(group==1);for _ in 0..9 {let v=s.fresh();a=s.xor(&a,&v);}forms.push(a);}
        let ab=s.and(&forms[0],&forms[1]);let bc=s.and(&forms[1],&forms[2]);
        let left=s.and(&ab,&forms[2]);let right=s.and(&forms[0],&bc);assert!(left==right);
        assert!(s.and(&left,&forms[0])==left);
        assert!(s.and(&left,&forms[0].complement()).is_zero());
        assert!(s.and(&left,&ab.complement()).is_zero());
    }
    #[test]
    fn native_xor_factor_reassociation_has_live_witness_and_phase(){
        let z=u64::MAX;let mut p=vec![];let mut r=Op::empty();r.kind=OperationType::Register;r.r_target=crate::circuit::RegisterId(0);p.push(r);
        for q in (0..27).chain(std::iter::once(35)) {let mut a=Op::empty();a.kind=OperationType::AppendToRegister;a.r_target=r.r_target;a.q_target=QubitId(q);p.push(a);}
        for group in 0..3 {for input in 0..9 {p.push(op(OperationType::CX,group*9+input,z,27+group));}}
        p.extend([op(OperationType::CCX,27,28,30),op(OperationType::CCX,30,29,31),op(OperationType::CCX,28,29,32),op(OperationType::CCX,27,32,35),op(OperationType::CZ,31,z,35)]);
        let q=witnesses(p.clone());assert_eq!(p.iter().filter(|o|o.kind==OperationType::CCX).count()-q.iter().filter(|o|o.kind==OperationType::CCX).count(),1);
        for batch in 0..4 {for phase in [0,u64::MAX,0xa5a5a5a5a5a5a5a5] {
            let mut xa=Word(0);let mut xb=Word(0);let mut a=Simulator::new(36,0,&mut xa);let mut b=Simulator::new(36,0,&mut xb);
            for input in 0..27 {a.qubits[input]=(0..64).fold(0u64,|v,l|v|((((batch*64+l)>>(input%8))&1)as u64)<<l);}
            a.qubits[35]=0xa5a5a5a5a5a5a5a5;b.qubits=a.qubits.clone();a.phase=phase;b.phase=phase;a.apply_iter(p.iter());b.apply_iter(q.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.phase,b.phase);
        }}
    }
'''
s=s[:-2]+tests+'}\n';p.write_text(s)
print('Factored immutable Boolean function nodes; canonical square-free AND union, exact complement absorption, bounded XOR interning. Probability-free algebra.')
