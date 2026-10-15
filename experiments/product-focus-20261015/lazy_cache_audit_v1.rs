use crate::circuit::{Op,OperationType as K,NO_QUBIT,NO_BIT};
use std::collections::{HashMap,HashSet};
#[derive(Clone,Debug)]
struct Window {uses:Vec<usize>,start:usize,end:usize,proxy:f64,donors:Vec<usize>}
fn touches(o:&Op)->Vec<usize>{
    if o.kind==K::R{return vec![];}
    [o.q_control1,o.q_control2,o.q_target].into_iter().filter(|q|*q!=NO_QUBIT).map(|q|q.0 as usize).collect()
}
pub fn audit(ops:&[Op]) {
    let nq=ops.iter().flat_map(touches).max().unwrap()+1;
    let mut depth=0usize;let mut fence=0usize;
    let mut starts=vec![0usize;ops.len()];let mut ends=vec![0usize;ops.len()];
    let mut weights=vec![0f64;ops.len()];
    for (i,o) in ops.iter().enumerate(){
        if depth==0 {fence=i;}starts[i]=fence;
        if o.kind==K::CCX {weights[i]=0.5f64.powi(depth as i32+if o.c_condition==NO_BIT{0}else{1});}
        match o.kind {K::PushCondition=>depth+=1,K::PopCondition=>depth-=1,_=>{}}
        ends[i]=if depth==0 {i+1}else{usize::MAX};
    }
    let mut next=vec![usize::MAX;nq];let mut end_ok=vec![false;ops.len()];let mut following=ops.len();
    for (i,o) in ops.iter().enumerate().rev(){
        if ends[i]!=usize::MAX {following=ends[i];}else{ends[i]=following;}
        if o.kind==K::CCX {end_ok[i]=[o.q_control1,o.q_control2].iter().all(|q|next[q.0 as usize]>=following);}
        match o.kind {K::X|K::CX|K::CCX|K::R|K::Hmr=>next[o.q_target.0 as usize]=i,
            K::Swap=>{next[o.q_target.0 as usize]=i;next[o.q_control1.0 as usize]=i;},_=>{}}
    }
    let mut symbolic=crate::interned_witness::Support::new(ops);
    let mut groups:HashMap<(bool,Vec<u64>),Vec<usize>>=HashMap::new();
    for (i,o) in ops.iter().enumerate(){
        if o.kind==K::CCX {groups.entry(symbolic.cache_product(o)).or_default().push(i);}
        symbolic.step(o);
    }
    let mut proposals=vec![];let mut repeated=0;let mut repetitions=0;
    for (_,mut uses) in groups {
        if uses.len()<2 {continue;}repeated+=1;repetitions+=uses.len()-1;
        while uses.len()>1&&!end_ok[*uses.last().unwrap()] {uses.pop();}
        if uses.len()<2 {continue;}
        let weight_sum=uses.iter().map(|i|weights[*i]).sum::<f64>();
        let union_proxy=1.0-uses.iter().map(|i|1.0-weights[*i]).product::<f64>();
        proposals.push(Window{start:starts[uses[0]],end:ends[*uses.last().unwrap()],uses,proxy:weight_sum-union_proxy,donors:vec![]});
    }
    proposals.sort_by_key(|w|(w.start,w.end));
    let startset:HashSet<_>=proposals.iter().map(|w|w.start).collect();
    let mut nexttouch=vec![usize::MAX;nq];let mut snap=HashMap::new();
    for (i,o) in ops.iter().enumerate().rev(){for q in touches(o){nexttouch[q]=i;}if startset.contains(&i){snap.insert(i,nexttouch.clone());}}
    symbolic=crate::interned_witness::Support::new(ops);let mut wi=0;
    for (i,o) in ops.iter().enumerate(){
        while wi<proposals.len()&&proposals[wi].start==i {
            let w=&mut proposals[wi];
            w.donors=symbolic.cache_zeros().into_iter().filter(|q|snap[&i][*q]>=w.end).collect();wi+=1;
        }
        symbolic.step(o);
    }
    assert_eq!(wi,proposals.len());
    let eligible=proposals.iter().filter(|w|!w.donors.is_empty()).count();
    let available_proxy: f64=proposals.iter().filter(|w|!w.donors.is_empty()).map(|w|w.proxy).sum();
    let mut occupied=vec![0usize;nq];let mut selected=0;let mut proxy=0.0;let mut used=HashSet::new();let mut structural=0;
    for w in proposals {
        if w.uses.iter().any(|i|used.contains(i)){continue;}
        if let Some(&donor)=w.donors.iter().find(|q|occupied[**q]<=w.start){
            occupied[donor]=w.end;selected+=1;proxy+=w.proxy;structural+=w.uses.len()-1;used.extend(w.uses.iter().copied());
            println!("LAZY_WINDOW donor={donor} start={} end={} proxy={} uses={:?}",w.start,w.end,w.proxy,w.uses);
        }
    }
    println!("LAZY_SUMMARY width={nq} repeated_groups={repeated} raw_repetitions={repetitions} eligible={eligible} selected={selected} available_proxy={available_proxy} selected_proxy={proxy} structural_repetitions={structural}");
}
