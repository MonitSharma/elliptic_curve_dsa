use crate::circuit::{Op,OperationType as K,QubitId,QubitOrBit,NO_QUBIT,NO_BIT,analyze_ops};
use std::collections::BTreeSet;
pub fn optimize(mut ops:Vec<Op>)->Vec<Op>{
    let (nq,_,_,registers)=analyze_ops(ops.iter());
    let mut pinned=BTreeSet::new();
    for reg in registers {for slot in reg {if let QubitOrBit::Qubit(q)=slot {pinned.insert(q.0 as usize);}}}
    let mut assigned=vec![None;nq as usize];let mut next=0u64;
    for &q in &pinned {assigned[q]=Some(next);next+=1;}
    let mut free=BTreeSet::new();let mut depth=0;
    for o in &mut ops {
        let old_target=o.q_target;
        for q in [&mut o.q_control1,&mut o.q_control2,&mut o.q_target] {
            if *q==NO_QUBIT {continue;}
            let old=q.0 as usize;
            let physical=if let Some(q)=assigned[old]{q}else{
                let q=if let Some(q)=free.pop_first(){q}else{let q=next;next+=1;q};
                assigned[old]=Some(q);q
            };*q=QubitId(physical);
        }
        // Only unconditional destructive resets terminate a lifetime. All
        // returned physical slots are exactly zero, for every measurement.
        if matches!(o.kind,K::R|K::Hmr)&&depth==0&&o.c_condition==NO_BIT&&!pinned.contains(&(old_target.0 as usize)) {
            assert!(free.insert(assigned[old_target.0 as usize].take().unwrap()));
        }
        if o.kind==K::PushCondition{depth+=1;}
        if o.kind==K::PopCondition{depth-=1;}
    }
    assert_eq!(depth,0);
    println!("LIFETIME_COMPACT old_width={nq} new_width={next} pinned={} free_at_end={}",pinned.len(),free.len());
    assert!(next<=nq);
    ops
}
