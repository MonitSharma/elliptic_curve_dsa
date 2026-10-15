use crate::circuit::{Op,OperationType as K,NO_QUBIT,NO_BIT};
use std::collections::HashMap;
#[derive(Clone,Debug)]
struct Window {a:usize,b:usize,uses:Vec<usize>,start:usize,end:usize,weight:f64,unconditional:usize}
pub fn audit(ops:&[Op]) {
    let nq=ops.iter().flat_map(|o|[o.q_control1,o.q_control2,o.q_target]).filter(|q|*q!=NO_QUBIT).map(|q|q.0 as usize).max().unwrap()+1;
    let mut depth=0usize;
    let mut fence=0usize;let mut starts=vec![0usize;ops.len()];let mut ends=vec![0usize;ops.len()];
    let mut prior=vec![usize::MAX;nq];let mut start_ok=vec![false;ops.len()];let mut weights=vec![0f64;ops.len()];
    for (i,o) in ops.iter().enumerate(){
        if depth==0 {fence=i;}starts[i]=fence;
        if o.kind==K::CCX {
            start_ok[i]=[o.q_control1,o.q_control2].iter().all(|q|prior[q.0 as usize]==usize::MAX||prior[q.0 as usize]<fence);
            weights[i]=0.5f64.powi(depth as i32+if o.c_condition==NO_BIT{0}else{1});
        }
        match o.kind {
            K::PushCondition=>depth+=1,K::PopCondition=>depth-=1,
            K::X|K::CX|K::CCX|K::R|K::Hmr=>prior[o.q_target.0 as usize]=i,
            K::Swap=>{prior[o.q_target.0 as usize]=i;prior[o.q_control1.0 as usize]=i;},_=>{}
        }
        ends[i]=if depth==0 {i+1}else{usize::MAX};
    }
    let mut next=vec![usize::MAX;nq];let mut end_ok=vec![false;ops.len()];let mut following=ops.len();
    for (i,o) in ops.iter().enumerate().rev(){
        if ends[i]!=usize::MAX {following=ends[i];}else{ends[i]=following;}
        if o.kind==K::CCX {end_ok[i]=[o.q_control1,o.q_control2].iter().all(|q|next[q.0 as usize]>=following);}
        match o.kind {K::X|K::CX|K::CCX|K::R|K::Hmr=>next[o.q_target.0 as usize]=i,
            K::Swap=>{next[o.q_target.0 as usize]=i;next[o.q_control1.0 as usize]=i;},_=>{}}
    }
    depth=0;
    let mut symbolic=crate::interned_witness::Support::new(ops);
    let mut groups:HashMap<(bool,Vec<u64>),Vec<usize>>=HashMap::new();
    for (i,o) in ops.iter().enumerate(){
        if o.kind==K::CCX {
            groups.entry(symbolic.cache_product(o)).or_default().push(i);
        }
        match o.kind {
            K::PushCondition=>depth+=1,
            K::PopCondition=>depth-=1,
            _=>{}
        }
        symbolic.step(o);
    }
    let mut proposals=vec![];let mut repeated=0;let mut repetitions=0;
    for (_,uses) in groups {
        if uses.len()<2 {continue;}repeated+=1;repetitions+=uses.len()-1;
        let a=ops[uses[0]].q_control1.0 as usize;let b=ops[uses[0]].q_control2.0 as usize;
        // Complete contiguous-subsequence family up to 64 occurrences. For
        // larger groups include adjacent pairs and the whole group explicitly.
        if uses.len()<=64 {
            for lo in 0..uses.len()-1 {for hi in lo+1..uses.len(){
                let part=&uses[lo..=hi];let w=part.iter().map(|i|weights[*i]).sum::<f64>()-1.0;
                if start_ok[part[0]]&&end_ok[*part.last().unwrap()]&&w>0.0 {
                    proposals.push(Window{a,b,uses:part.to_vec(),start:starts[part[0]],end:ends[*part.last().unwrap()],weight:w,unconditional:part.iter().filter(|i|weights[**i]==1.0).count()});
                }
            }}
        } else {
            panic!("Large group needs bounded candidate enumeration before interpreting results");
        }
    }
    proposals.sort_by_key(|w|w.end);
    let ends:Vec<_>=proposals.iter().map(|w|w.end).collect();
    let mut dp=vec![0f64;proposals.len()+1];let mut take=vec![None;proposals.len()+1];
    for (i,w) in proposals.iter().enumerate(){
        let prev=ends[..i].partition_point(|end|*end<=w.start);
        let score=dp[prev]+w.weight;
        if score>dp[i] {dp[i+1]=score;take[i+1]=Some(prev);}else{dp[i+1]=dp[i];}
    }
    let mut at=proposals.len();let mut selected=vec![];
    while at>0 {if let Some(prev)=take[at] {selected.push(proposals[at-1].clone());at=prev;}else{at-=1;}}
    selected.reverse();
    println!("CACHE_SUMMARY base_width={nq} candidate_width={} repeated_groups={repeated} raw_repetitions={repetitions} proposals={} selected={} depth_proxy_saving={} unconditional_lower_bound={}",nq+1,proposals.len(),selected.len(),dp.last().unwrap(),selected.iter().map(|w|w.unconditional as i64-1).sum::<i64>());
    for w in selected {println!("CACHE_WINDOW a={} b={} start={} end={} proxy={} uses={:?}",w.a,w.b,w.start,w.end,w.weight,w.uses);}
}
