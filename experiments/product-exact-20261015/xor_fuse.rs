//! Exact deferred XOR aggregation for commuting repeated Toffolis. No quantum
//! scratch: save each original classical guard into an XOR accumulator and
//! apply the product once under the parity of those guards.
use crate::circuit::{Op,OperationType as K,BitId,NO_BIT,NO_QUBIT};
use std::collections::HashMap;
fn gate(k:K,bit:u64)->Op {let mut o=Op::empty();o.kind=k;if k==K::PushCondition{o.c_condition=BitId(bit);}else{o.c_target=BitId(bit);}o}
pub fn optimize(ops:Vec<Op>)->Vec<Op>{
    let nq=ops.iter().flat_map(|o|[o.q_control1,o.q_control2,o.q_target]).filter(|q|*q!=NO_QUBIT).map(|q|q.0 as usize).max().unwrap()+1;
    let nb=ops.iter().flat_map(|o|[o.c_condition,o.c_target]).filter(|b|*b!=NO_BIT).map(|b|b.0).max().unwrap()+1;
    let mut starts=vec![0;ops.len()];let mut ends=vec![usize::MAX;ops.len()];let(mut depth,mut fence)=(0,0);
    for (i,o) in ops.iter().enumerate(){if depth==0{fence=i;}starts[i]=fence;if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth-=1;}if depth==0{ends[i]=i+1;}}
    let mut after=ops.len();let mut nw=vec![usize::MAX;nq];let mut nr=vec![usize::MAX;nq];let mut end_ok=vec![false;ops.len()];
    for (i,o) in ops.iter().enumerate().rev(){if ends[i]!=usize::MAX{after=ends[i];}else{ends[i]=after;}
        if o.kind==K::CCX{end_ok[i]=nw[o.q_control1.0 as usize]>=after&&nw[o.q_control2.0 as usize]>=after&&nr[o.q_target.0 as usize]>=after;}
        update(o,i,&mut nw,&mut nr);
    }
    let mut lw=vec![None;nq];let mut lr=vec![None;nq];let mut active=HashMap::<(u64,u64,u64),usize>::new();let mut groups=Vec::<Vec<usize>>::new();
    for (i,o) in ops.iter().enumerate(){
        if o.kind==K::CCX{
            let a=o.q_control1.0.min(o.q_control2.0);let b=o.q_control1.0.max(o.q_control2.0);let t=o.q_target.0;let key=(a,b,t);
            let previous=active.get(&key).copied().filter(|&g|{let p=*groups[g].last().unwrap();[lw[a as usize],lw[b as usize],lr[t as usize]].into_iter().all(|x|x.map_or(true,|j|j<=p))});
            if let Some(g)=previous{groups[g].push(i);}else{let g=groups.len();groups.push(vec![i]);active.insert(key,g);}
        }
        let mut write=|q:crate::circuit::QubitId|{if q!=NO_QUBIT{lw[q.0 as usize]=Some(i);}};
        let mut read=|q:crate::circuit::QubitId|{if q!=NO_QUBIT{lr[q.0 as usize]=Some(i);}};
        match o.kind{
            K::X=>write(o.q_target),
            K::CX|K::CCX=>{write(o.q_target);read(o.q_control1);read(o.q_control2);},
            K::R|K::Hmr=>{write(o.q_target);read(o.q_target);},
            K::Swap=>{write(o.q_target);write(o.q_control1);read(o.q_target);read(o.q_control1);},
            K::Z|K::CZ|K::CCZ=>{read(o.q_target);read(o.q_control1);read(o.q_control2);},
            _=>{}
        }
    }
    let mut windows=vec![];
    for mut us in groups{while us.len()>1&&!end_ok[*us.last().unwrap()]{us.pop();}if us.len()>1{windows.push(us);}}
    windows.sort();let mut begin=HashMap::<usize,Vec<usize>>::new();let mut end=HashMap::<usize,Vec<usize>>::new();let mut used=HashMap::new();
    for (g,us) in windows.iter().enumerate(){begin.entry(starts[us[0]]).or_default().push(g);end.entry(ends[*us.last().unwrap()]).or_default().push(g);for &i in us{assert!(used.insert(i,g).is_none());}}
    let mut out=Vec::with_capacity(ops.len()+windows.len()*4);
    for i in 0..=ops.len(){
        if let Some(gs)=end.get(&i){for &g in gs{let bit=nb+g as u64;let mut o=ops[*windows[g].last().unwrap()];o.c_condition=BitId(bit);out.push(o);out.push(gate(K::BitStore0,bit));}}
        if let Some(gs)=begin.get(&i){for &g in gs{out.push(gate(K::BitStore0,nb+g as u64));}}
        if i==ops.len(){break;}let o=ops[i];if let Some(&g)=used.get(&i){let mut x=gate(K::BitInvert,nb+g as u64);x.c_condition=o.c_condition;out.push(x);}else{out.push(o);}
    }
    println!("XOR_FUSE windows={} merged_uses={} old_ops={} new_ops={}",windows.len(),windows.iter().map(Vec::len).sum::<usize>(),ops.len(),out.len());out
}
fn update(o:&Op,i:usize,w:&mut[usize],r:&mut[usize]){
    let mut write=|q:crate::circuit::QubitId|{if q!=NO_QUBIT{w[q.0 as usize]=i;}};
    let mut read=|q:crate::circuit::QubitId|{if q!=NO_QUBIT{r[q.0 as usize]=i;}};
    match o.kind{
        K::X=>write(o.q_target),
        K::CX|K::CCX=>{write(o.q_target);read(o.q_control1);read(o.q_control2);},
        K::R|K::Hmr=>{write(o.q_target);read(o.q_target);},
        K::Swap=>{write(o.q_target);write(o.q_control1);read(o.q_target);read(o.q_control1);},
        K::Z|K::CZ|K::CCZ=>{read(o.q_target);read(o.q_control1);read(o.q_control2);},
        _=>{}
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use crate::circuit::{QubitId,RegisterId};
    use quantum_ecc::sim::Simulator;
    struct Zero;
    impl sha3::digest::XofReader for Zero{fn read(&mut self,out:&mut[u8]){out.fill(0);}}
    fn program()->Vec<Op>{
        let mut p=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=RegisterId(0);p.push(r);
        for q in 0..3 {let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=r.r_target;o.q_target=QubitId(q);p.push(o);}
        for b in 0..4 {let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=r.r_target;o.c_target=BitId(b);p.push(o);}
        for b in 0..4 {let mut o=Op::empty();o.kind=K::CCX;o.q_control1=QubitId(0);o.q_control2=QubitId(1);o.q_target=QubitId(2);o.c_condition=BitId(b);p.push(o);}p
    }
    #[test]
    fn xor_guard_fusion_all_inputs_dirty_scratch_and_phase(){
        let p=program();let q=optimize(p.clone());assert_eq!(q.iter().filter(|o|o.kind==K::CCX).count(),1);
        for batch in 0..2 {for phase in [0,u64::MAX,0xa5a5a5a5a5a5a5a5] {
            let mut za=Zero;let mut zb=Zero;let mut a=Simulator::new(3,4,&mut za);let mut b=Simulator::new(3,5,&mut zb);
            for bit in 0..7 {let v=(0..64).fold(0u64,|v,l|v|(((((batch*64+l)>>bit)&1) as u64)<<l));if bit<3{a.qubits[bit]=v;}else{a.bits[bit-3]=v;}}
            b.qubits=a.qubits.clone();b.bits[..4].copy_from_slice(&a.bits);b.bits[4]=u64::MAX;a.phase=phase;b.phase=phase;
            a.apply_iter(p.iter());b.apply_iter(q.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits[..4]);assert_eq!(a.phase,b.phase);assert_eq!(b.bits[4],0);assert!(b.stats.toffoli_gates<=a.stats.toffoli_gates);
        }}
    }
    #[test]
    fn target_phase_reader_blocks_fusion(){
        let mut p=program();let mut z=Op::empty();z.kind=K::Z;z.q_target=QubitId(2);
        for at in (9..12).rev(){p.insert(at,z);}
        assert_eq!(optimize(p.clone()),p);
    }
}
