//! Commute unconditional destructive measurements/resets to the first global
//! condition boundary after their last quantum/classical dependency. No gate
//! using the target or result bit is crossed.
use crate::circuit::{Op,OperationType as K,NO_BIT,NO_QUBIT};
use std::collections::HashMap;
pub fn optimize(ops:Vec<Op>)->Vec<Op>{
    let nq=ops.iter().flat_map(|o|[o.q_control1,o.q_control2,o.q_target]).filter(|q|*q!=NO_QUBIT).map(|q|q.0 as usize).max().unwrap()+1;
    let nb=ops.iter().flat_map(|o|[o.c_condition,o.c_target]).filter(|b|*b!=NO_BIT).map(|b|b.0 as usize).max().unwrap()+1;
    let mut boundaries=vec![0];let mut depth=0;let mut before_depth=Vec::with_capacity(ops.len());
    for(i,o)in ops.iter().enumerate(){before_depth.push(depth);if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth-=1;}if depth==0{boundaries.push(i+1);}}
    assert_eq!(depth,0);let mut lastq=vec![None;nq];let mut lastb=vec![None;nb];
    let mut moved=HashMap::<usize,Vec<(usize,Op)>>::new();let mut omit=vec![false;ops.len()];let(mut count,mut distance)=(0,0);
    for(i,o)in ops.iter().enumerate(){
        if matches!(o.kind,K::R|K::Hmr)&&o.c_condition==NO_BIT&&before_depth[i]==0{
            let mut after=lastq[o.q_target.0 as usize].map_or(0,|j|j+1);
            if o.c_target!=NO_BIT{after=after.max(lastb[o.c_target.0 as usize].map_or(0,|j|j+1));}
            let at=boundaries[boundaries.partition_point(|j|*j<after)];
            if at<i{moved.entry(at).or_default().push((i,*o));omit[i]=true;count+=1;distance+=i-at;}
        }
        for q in [o.q_control1,o.q_control2,o.q_target].into_iter().filter(|q|*q!=NO_QUBIT){lastq[q.0 as usize]=Some(i);}
        for b in [o.c_condition,o.c_target].into_iter().filter(|b|*b!=NO_BIT){lastb[b.0 as usize]=Some(i);}
    }
    let mut out=Vec::with_capacity(ops.len());let mut origins=Vec::new();
    for i in 0..=ops.len(){
        if let Some(ms)=moved.get(&i){for &(old,o)in ms{out.push(o);origins.push(old);}}
        if i==ops.len(){break;}if !omit[i]{out.push(ops[i]);if matches!(ops[i].kind,K::R|K::Hmr){origins.push(i);}}
    }
    assert_eq!(out.len(),ops.len());
    println!("EARLY_RESET moved={count} total_operation_distance={distance} identical_gate_multiset=true");
    if let Ok(path)=std::env::var("EARLY_RESET_EVENT_MAP"){std::fs::write(path,origins.iter().map(|x|x.to_string()).collect::<Vec<_>>().join("\n")).unwrap();}
    out
}
#[cfg(test)]
mod tests{
    use super::*;
    use crate::circuit::{QubitId,BitId,RegisterId};
    use quantum_ecc::sim::Simulator;
    struct Word(u64);impl sha3::digest::XofReader for Word{fn read(&mut self,out:&mut[u8]){out.copy_from_slice(&self.0.to_le_bytes());}}
    #[test]
    fn early_measurement_commutes_with_unrelated_control_updates_all_inputs(){
        let mut p=vec![];let mut reg=Op::empty();reg.kind=K::Register;reg.r_target=RegisterId(0);p.push(reg);
        for q in [0,1,3]{let mut o=Op::empty();o.kind=K::AppendToRegister;o.q_target=QubitId(q);o.r_target=reg.r_target;p.push(o);}
        let gate=|k,a,b,t|{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o};
        p.push(gate(K::CCX,0,1,2));p.push(gate(K::CX,2,u64::MAX,3));p.push(gate(K::CX,0,u64::MAX,1));p.push(gate(K::X,u64::MAX,u64::MAX,4));
        let mut h=gate(K::Hmr,u64::MAX,u64::MAX,2);h.c_target=BitId(0);p.push(h);
        let mut z=gate(K::CZ,0,u64::MAX,1);z.c_condition=BitId(0);p.push(z);
        let q=optimize(p.clone());assert_ne!(q,p);assert_eq!(q.iter().position(|o|o.kind==K::Hmr),Some(6));
        for input in 0..8{for word in [0,u64::MAX,0xa5a5a5a5a5a5a5a5]{
            let mut xa=Word(word);let mut xb=Word(word);let mut a=Simulator::new(5,1,&mut xa);let mut b=Simulator::new(5,1,&mut xb);
            for(bit,q)in [0,1,3].into_iter().enumerate(){a.qubits[q]=if input>>bit&1==1{u64::MAX}else{0};}b.qubits=a.qubits.clone();a.phase=word;b.phase=word;
            a.apply_iter(p.iter());b.apply_iter(q.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);
        }}
    }
}
