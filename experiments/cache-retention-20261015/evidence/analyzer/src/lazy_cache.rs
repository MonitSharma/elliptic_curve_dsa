use crate::circuit::{Op,OperationType as K,QubitId,BitId,NO_QUBIT,NO_BIT};
use std::collections::{HashMap,HashSet};
#[derive(Clone,Debug)]
struct Window {uses:Vec<usize>,start:usize,end:usize,proxy:f64,donors:Vec<usize>}
fn touches(o:&Op)->Vec<usize>{
    if o.kind==K::R{return vec![];}
    [o.q_control1,o.q_control2,o.q_target].into_iter().filter(|q|*q!=NO_QUBIT).map(|q|q.0 as usize).collect()
}
pub fn optimize(ops:Vec<Op>)->Vec<Op> {
    let nq=ops.iter().flat_map(|o|[o.q_control1,o.q_control2,o.q_target]).filter(|q|*q!=NO_QUBIT).map(|q|q.0 as usize).max().unwrap()+1;
    let nb=ops.iter().flat_map(|o|[o.c_target,o.c_condition]).filter(|b|*b!=NO_BIT).map(|b|b.0).max().map_or(0,|b|b+1);
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
    let mut symbolic=super::interned_witness::Support::new(&ops);
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
    proposals.sort_by(|a,b|(a.start,a.end,&a.uses).cmp(&(b.start,b.end,&b.uses)));

    // All new quantum slots are initially clean. Reuse a slot only after its
    // earlier lease has measured it to zero and discharged the phase.
    let eligible=proposals.len();
    let mut free_after=Vec::<usize>::new();
    let mut chosen=vec![];
    for w in proposals {
        let slot=free_after.iter().position(|end|*end<=w.start).unwrap_or_else(||{
            free_after.push(0);free_after.len()-1
        });
        free_after[slot]=w.end;let donor=nq+slot;
        println!("LAZY_WINDOW donor={donor} start={} end={} proxy={} uses={:?}",w.start,w.end,w.proxy,w.uses);
        chosen.push((donor,w));
    }
    let width=nq+free_after.len();
    println!("LAZY_SUMMARY base_width={nq} width={width} repeated_groups={repeated} raw_repetitions={repetitions} eligible={eligible} selected={}",chosen.len());
    render(ops,chosen,nb,width)
}

fn gate(k:K,a:Option<u64>,b:Option<u64>,t:Option<u64>,bt:Option<u64>,c:Option<u64>)->Op {
    let mut o=Op::empty();o.kind=k;
    o.q_control1=QubitId(a.unwrap_or(u64::MAX));o.q_control2=QubitId(b.unwrap_or(u64::MAX));o.q_target=QubitId(t.unwrap_or(u64::MAX));
    o.c_target=BitId(bt.unwrap_or(u64::MAX));o.c_condition=BitId(c.unwrap_or(u64::MAX));o.validate();o
}
fn store(bit:u64,value:bool)->Op {gate(if value{K::BitStore1}else{K::BitStore0},None,None,None,Some(bit),None)}
fn push(bit:u64)->Op {gate(K::PushCondition,None,None,None,None,Some(bit))}
fn pop()->Op {gate(K::PopCondition,None,None,None,None,None)}

fn render(ops:Vec<Op>,chosen:Vec<(usize,Window)>,nb:u64,nq:usize)->Vec<Op>{
    let mut starts:HashMap<usize,Vec<usize>>=HashMap::new();let mut ends:HashMap<usize,Vec<usize>>=HashMap::new();let mut uses=HashMap::new();
    for (j,(_,w)) in chosen.iter().enumerate(){
        starts.entry(w.start).or_default().push(j);ends.entry(w.end).or_default().push(j);
        for &i in &w.uses {assert!(uses.insert(i,j).is_none());}
    }
    let mut active=vec![None;nq];let mut out=Vec::with_capacity(ops.len()+chosen.len()*25);let mut dropped_resets=0;
    for i in 0..=ops.len(){
        // End before start: adjacent leases may reuse the same physical wire.
        if let Some(js)=ends.get(&i){for &j in js {
            let (q,w)=&chosen[j];let valid=nb+3*j as u64;let temp=valid+1;let m=valid+2;
            let last=ops[*w.uses.last().unwrap()];
            out.push(push(valid));out.push(gate(K::Hmr,None,None,Some(*q as u64),Some(m),None));
            out.push(gate(K::CZ,Some(last.q_control1.0),None,Some(last.q_control2.0),None,Some(m)));out.push(pop());
            out.extend([store(valid,false),store(temp,false),store(m,false)]);
            assert_eq!(active[*q],Some(j));active[*q]=None;
        }}
        if let Some(js)=starts.get(&i){for &j in js {
            let (q,_)=&chosen[j];assert!(active[*q].is_none());active[*q]=Some(j);
            for b in nb+3*j as u64..nb+3*j as u64+3 {out.push(store(b,false));}
        }}
        if i==ops.len(){break;}let o=ops[i];
        if let Some(&j)=uses.get(&i){
            let q=chosen[j].0 as u64;let valid=nb+3*j as u64;let temp=valid+1;
            if o.c_condition!=NO_BIT {out.push(push(o.c_condition.0));}
            out.push(store(temp,true));out.push(gate(K::BitInvert,None,None,None,Some(temp),Some(valid)));
            out.push(push(temp));out.push(gate(K::CCX,Some(o.q_control1.0),Some(o.q_control2.0),Some(q),None,None));
            out.push(store(valid,true));out.push(pop());
            out.push(gate(K::CX,Some(q),None,Some(o.q_target.0),None,None));out.push(store(temp,false));
            if o.c_condition!=NO_BIT {out.push(pop());}
        }else if o.kind==K::R&&active[o.q_target.0 as usize].is_some(){
            // This wire was proved zero and otherwise untouched in the original
            // stream throughout the lease. Its original reset had no effect.
            dropped_resets+=1;
        }else{out.push(o);}
    }
    assert!(active.iter().all(|x|x.is_none()));
    println!("LAZY_RENDER windows={} dropped_original_zero_resets={dropped_resets} old_ops={} new_ops={}",chosen.len(),ops.len(),out.len());out
}

pub fn audit(ops:&[Op]) {let _=optimize(ops.to_vec());}
#[cfg(test)]
mod tests{
use super::*;
use crate::circuit::{analyze_ops,RegisterId};
use quantum_ecc::sim::Simulator;
struct Events{pattern:usize,at:usize}
impl sha3::digest::XofReader for Events{fn read(&mut self,out:&mut[u8]){
assert_eq!(out.len(),8);let w=if self.pattern>>self.at&1==0{0u64}else{u64::MAX};
self.at+=1;out.copy_from_slice(&w.to_le_bytes());}}
fn program()->Vec<Op>{
let mut p=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=RegisterId(0);p.push(r);
for q in 0..4{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);p.push(o);}
for b in 0..4{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.c_target=BitId(b);p.push(o);}
p.extend([
gate(K::CCX,Some(0),Some(1),Some(3),None,Some(0)),
gate(K::CCX,Some(1),Some(2),Some(3),None,Some(1)),
gate(K::X,None,None,Some(0),None,None),
gate(K::X,None,None,Some(0),None,None),
gate(K::CCX,Some(0),Some(1),Some(3),None,Some(2)),
gate(K::CCX,Some(1),Some(2),Some(3),None,Some(3))]);p}
fn check(p:&[Op],q:&[Op])->bool{
let (nq,nb,_,_)=analyze_ops(q.iter());assert!(nq>4);
let mr=q.iter().filter(|o|matches!(o.kind,K::Hmr|K::R)).count();assert_eq!(mr,2);
let mut ok=true;let mut saved=0;
for pattern in 0..4{for batch in 0..4{
let mut xa=Events{pattern:0,at:0};let mut xb=Events{pattern,at:0};
let mut a=Simulator::new(4,4,&mut xa);let mut b=Simulator::new(nq as usize,nb as usize,&mut xb);
for bit in 0..8{let v=(0..64).fold(0u64,|v,l|v|(((((batch*64+l)>>bit)&1)as u64)<<l));
if bit<4{a.qubits[bit]=v;b.qubits[bit]=v;}else{a.bits[bit-4]=v;b.bits[bit-4]=v;}}
for x in &mut b.bits[4..]{*x=0xa5a5a5a5a5a5a5a5;}
a.phase=0x55aa55aa55aa55aa;b.phase=a.phase;
a.apply_iter(p.iter());b.apply_iter(q.iter());
ok&=a.qubits==b.qubits[..4]&&a.bits==b.bits[..4]&&a.phase==b.phase;
ok&=b.qubits[4..].iter().all(|v|*v==0)&&b.bits[4..].iter().all(|v|*v==0);
assert!(b.stats.toffoli_gates<=a.stats.toffoli_gates);saved+=a.stats.toffoli_gates-b.stats.toffoli_gates;
}}
assert!(saved>0);ok}
#[test]fn wide_cache_all_inputs_and_measurements(){let p=program();let q=optimize(p.clone());
assert_eq!(q,optimize(p.clone()));assert!(check(&p,&q));println!("WIDE_NATIVE cases=1024 independent_outcomes=4 clean_new_quantum=true dirty_classical=true");}
#[test]fn wide_cache_phase_fault_detected(){let p=program();let mut q=optimize(p.clone());
let i=q.iter().position(|o|o.kind==K::CZ).unwrap();q.remove(i);assert!(!check(&p,&q));}
}
