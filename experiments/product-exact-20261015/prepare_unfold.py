from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
dest=root/'unfold-tool'
shutil.copytree(root/'analyzer',dest,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
path=dest/'src/interned_anf_retained.rs'
text=path.read_text()
text=text.replace('    large_xors: std::collections::HashMap<Vec<u64>,u64>,','    large_xors: std::collections::HashMap<Vec<u64>,u64>,\n    large_defs: std::collections::HashMap<u64,Vec<u64>>,')
text=text.replace('            large_xors: std::collections::HashMap::new(),','            large_xors: std::collections::HashMap::new(),\n            large_defs: std::collections::HashMap::new(),')
needle='        if atoms.len() > atom_cap() {'
assert text.count(needle)==1
text=text.replace(needle,'''        // Expand only a bounded small XOR of existing immutable definitions.
        // Forgetting a definition merely loses this normalization opportunity.
        // Constants remain outside every definition and cache key.
        if atoms.len()<=16 && atoms.iter().any(|id|self.large_defs.contains_key(id)) {
            let budget=atom_cap().saturating_mul(4);
            let count:usize=atoms.iter().map(|id|self.large_defs.get(id).map_or(1,|d|d.len())).sum();
            if count<=budget {
                let mut flat=std::collections::BTreeSet::new();
                for id in atoms {
                    if let Some(def)=self.large_defs.get(&id) {
                        for &term in def {if !flat.insert(term){flat.remove(&term);}}
                    } else if !flat.insert(id){flat.remove(&id);}
                }
                atoms=flat.into_iter().collect();
            }
        }
'''+needle)
old='''        if self.large_xors.len()>=50000{self.large_xors.clear();}
        let id=if let Some(&id)=self.large_xors.get(&atoms){id}else{let id=self.fresh().atoms[0];self.large_xors.insert(atoms,id);id};'''
new='''        if self.large_xors.len()>=50000{self.large_xors.clear();self.large_defs.clear();}
        let id=if let Some(&id)=self.large_xors.get(&atoms){id}else{let id=self.fresh().atoms[0];self.large_defs.insert(id,atoms.clone());self.large_xors.insert(atoms,id);id};'''
assert text.count(old)==1
text=text.replace(old,new)
text+='''
#[cfg(test)]
mod unfold_tests {
    use super::*;
    #[test]
    fn retained_xor_cancellation_and_complement_exact_ids() {
        let mut s=Support::new(&[]);let mut base=vec![];
        for _ in 0..atom_cap()+4 {base.push(s.fresh().atoms[0]);}
        let left=s.retain_large(false,base[..atom_cap()+1].to_vec());
        let mut terms=base[..atom_cap()].to_vec();terms.push(base[atom_cap()+1]);
        let right=s.retain_large(true,terms);
        let got=s.xor(&left,&right);
        assert!(got.constant);assert_eq!(got.atoms,base[atom_cap()..atom_cap()+2]);
        let twice=s.xor(&got,&right);let restored=s.xor(&twice,&left);assert!(restored.is_zero());
        // Cache erasure never changes a live ID's meaning or recycles it.
        s.large_xors.clear();s.large_defs.clear();let unknown=s.xor(&left,&right);
        assert!(unknown.atoms!=got.atoms);assert!(unknown.constant);
    }
    struct Word(u64);
    impl sha3::digest::XofReader for Word {fn read(&mut self,out:&mut[u8]){out.copy_from_slice(&self.0.to_le_bytes());}}
    fn gate(k:OperationType,a:u64,b:u64,t:u64)->Op {let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o}
    #[test]
    fn restored_large_xor_exposes_distributive_witness_native_phase() {
        use quantum_ecc::sim::Simulator;
        let n=atom_cap();let z=u64::MAX;let a=(n+3)as u64;let b=a+1;let w=b+1;let target=w+1;
        let mut p=vec![];let mut r=Op::empty();r.kind=OperationType::Register;r.r_target=crate::circuit::RegisterId(0);p.push(r);
        for i in 0..n+3 {let mut o=Op::empty();o.kind=OperationType::AppendToRegister;o.r_target=r.r_target;o.q_target=QubitId(i as u64);p.push(o);}
        for i in 0..n+1 {p.push(gate(OperationType::CX,i as u64,z,a));}
        for i in 0..n {p.push(gate(OperationType::CX,i as u64,z,b));}
        p.push(gate(OperationType::CX,(n+1)as u64,z,b));p.push(gate(OperationType::CX,b,z,a));
        p.push(gate(OperationType::CCX,n as u64,(n+2)as u64,w));p.push(gate(OperationType::CCX,(n+1)as u64,(n+2)as u64,w));p.push(gate(OperationType::CCX,a,(n+2)as u64,target));
        let q=witnesses(p.clone());assert!(q.len()==p.len());assert_eq!(q.iter().filter(|o|o.kind==OperationType::CCX).count()+1,p.iter().filter(|o|o.kind==OperationType::CCX).count());
        let mut rng=0x123456789abcdefu64;
        for _ in 0..16 {let(mut xa,mut xb)=(Word(0),Word(0));let mut x=Simulator::new(target as usize+1,0,&mut xa);let mut y=Simulator::new(target as usize+1,0,&mut xb);
            for i in 0..n+3 {rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;x.qubits[i]=rng;}x.phase=rng;y.qubits=x.qubits.clone();y.phase=x.phase;
            x.apply_iter(p.iter());y.apply_iter(q.iter());assert_eq!(x.qubits,y.qubits);assert_eq!(x.phase,y.phase);
        }
    }
}
'''
path.write_text(text)
