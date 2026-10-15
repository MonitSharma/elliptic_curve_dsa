use crate::circuit::{Op,OperationType as K,NO_QUBIT,NO_BIT};
use std::collections::HashMap;
#[derive(Clone,Debug)]
struct Window {a:usize,b:usize,uses:Vec<usize>}
pub fn audit(ops:&[Op]) {
    let nq=ops.iter().flat_map(|o|[o.q_control1,o.q_control2,o.q_target]).filter(|q|*q!=NO_QUBIT).map(|q|q.0 as usize).max().unwrap()+1;
    let mut generation=vec![0usize;nq];let mut depth=0usize;
    let mut groups:HashMap<(usize,usize,usize,usize),Vec<usize>>=HashMap::new();
    for (i,o) in ops.iter().enumerate(){
        if o.kind==K::CCX&&depth==0&&o.c_condition==NO_BIT {
            let mut a=o.q_control1.0 as usize;let mut b=o.q_control2.0 as usize;
            if a>b {std::mem::swap(&mut a,&mut b);}
            groups.entry((a,b,generation[a],generation[b])).or_default().push(i);
        }
        match o.kind {
            K::PushCondition=>depth+=1,
            K::PopCondition=>depth-=1,
            K::X|K::CX|K::CCX|K::R|K::Hmr=>generation[o.q_target.0 as usize]+=1,
            K::Swap=>{generation[o.q_target.0 as usize]+=1;generation[o.q_control1.0 as usize]+=1;},
            _=>{}
        }
    }
    let mut proposals=vec![];let mut repeated=0;let mut repetitions=0;
    for ((a,b,_,_),uses) in groups {
        if uses.len()<2 {continue;}repeated+=1;repetitions+=uses.len()-1;
        // Complete contiguous-subsequence family up to 64 occurrences. For
        // larger groups include adjacent pairs and the whole group explicitly.
        if uses.len()<=64 {
            for lo in 0..uses.len()-1 {for hi in lo+1..uses.len(){proposals.push(Window{a,b,uses:uses[lo..=hi].to_vec()});}}
        } else {
            for pair in uses.windows(2){proposals.push(Window{a,b,uses:pair.to_vec()});}
            proposals.push(Window{a,b,uses});
        }
    }
    proposals.sort_by_key(|w|*w.uses.last().unwrap());
    let ends:Vec<_>=proposals.iter().map(|w|*w.uses.last().unwrap()).collect();
    let mut dp=vec![0usize;proposals.len()+1];let mut take=vec![None;proposals.len()+1];
    for (i,w) in proposals.iter().enumerate(){
        let prev=ends[..i].partition_point(|end|*end<w.uses[0]);
        let score=dp[prev]+w.uses.len()-1;
        if score>dp[i] {dp[i+1]=score;take[i+1]=Some(prev);}else{dp[i+1]=dp[i];}
    }
    let mut at=proposals.len();let mut selected=vec![];
    while at>0 {if let Some(prev)=take[at] {selected.push(proposals[at-1].clone());at=prev;}else{at-=1;}}
    selected.reverse();
    println!("CACHE_SUMMARY base_width={nq} candidate_width={} repeated_groups={repeated} raw_repetitions={repetitions} proposals={} selected={} unconditional_toffoli_saving={}",nq+1,proposals.len(),selected.len(),dp.last().unwrap());
    for w in selected {println!("CACHE_WINDOW a={} b={} uses={:?}",w.a,w.b,w.uses);}
}
