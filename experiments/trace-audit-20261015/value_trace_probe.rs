//! Observation-only attribution of deterministic value failures to leapfrog walk rails
//! (trace-value-20261015). Extends rail-repair-20261015/rail_trace.rs with reverse-tick
//! restoration and endpoint checks. Gate-inert: marks only record op indices and wire IDs.
//! Diagnostic only; score=NONE.
use crate::circuit::{analyze_ops, Op, QubitId};
use alloy_primitives::U256;
use sha3::{Shake256,digest::{Update,ExtendableOutput}};
use std::{collections::HashMap,sync::Mutex};

#[derive(Clone,Copy,PartialEq,Debug)]
pub enum Kind { FwdBefore, FwdAfter, RevBefore, RevAfter }
#[derive(Clone)]
struct Mark { at:usize, phase:&'static str, tick:usize, kind:Kind, rails:[Vec<QubitId>;2], letter:Vec<QubitId>, low:bool }
static MARKS:Mutex<Vec<Mark>>=Mutex::new(Vec::new());

pub fn mark(at:usize,phase:&'static str,tick:usize,kind:Kind,rails:&[Vec<QubitId>;2],letter:&[QubitId],low:bool){
    if rails[0].is_empty()||rails[1].is_empty(){ return; }
    MARKS.lock().unwrap().push(Mark{at,phase,tick,kind,rails:rails.clone(),letter:letter.to_vec(),low});
}
fn sub(a:U256,b:U256,p:U256)->U256{if a>=b{a-b}else{p-(b-a)}}
// Rail value as a field element: two's complement top bit, bits >=256 folded by f=2^32+977,
// optional parked low bit (value = 2*v+1). Copied from rail_trace.rs.
fn word(qs:&[QubitId],words:&[u64],lane:usize,p:U256,low:bool)->U256{
    let f=U256::from(0x1000003d1u64);let mut v=U256::ZERO;
    for(i,q)in qs.iter().enumerate(){if words[q.0 as usize]>>lane&1!=0{
        let bit=if i<256{U256::from(1)<<i}else{f<<(i-256)};
        v=v.add_mod(bit,p);
    }}
    if words[qs.last().unwrap().0 as usize]>>lane&1!=0{
        let pow=if qs.len()<256{U256::from(1)<<qs.len()}else{f<<(qs.len()-256)};v=sub(v,pow,p);
    }
    if low{v=v.add_mod(v,p).add_mod(U256::from(1),p);}v
}
fn half(v:U256,p:U256)->U256{if v.bit(0){(v>>1)+(p>>1)+U256::from(1)}else{v>>1}}

pub fn run(ops:&[Op]){
    let root="/home/hclau/ecdsa_research/trace-value-20261015";
    let(nq,nb,_,regs)=analyze_ops(ops.iter());let p=super::SECP256K1_P;
    let marks=MARKS.lock().unwrap().clone();
    let mut last_tick=HashMap::<&str,usize>::new();
    for m in &marks{ if m.kind==Kind::FwdAfter { let e=last_tick.entry(m.phase).or_insert(0); *e=(*e).max(m.tick);} }
    let kinds=marks.iter().fold(HashMap::<String,usize>::new(),|mut h,m|{*h.entry(format!("{}:{:?}",m.phase,m.kind)).or_insert(0)+=1;h});
    eprintln!("TRACE_MARKS total={} by_kind={:?} last_tick={:?}",marks.len(),kinds,last_tick);
    let one=U256::from(1);
    for family in ["valuefail186","independent"]{
        let text=std::fs::read_to_string(format!("{root}/packets/{family}.tsv")).unwrap();
        let points:Vec<[U256;6]>=text.lines().filter(|l|!l.trim().is_empty()).map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
        let mut summary=HashMap::<String,usize>::new();
        for(batch,rows)in points.chunks(64).enumerate(){
            let mut h=Shake256::default();h.update(b"trace-value-20261015");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut ref_rng=rng.clone();
            let mut sim=super::observed_sim::Simulator::new(nq as usize,nb as usize,&mut rng);
            let mut reference=crate::sim::Simulator::new(nq as usize,nb as usize,&mut ref_rng);
            for(lane,v)in rows.iter().enumerate(){for k in 0..4{sim.set_register(&regs[k],v[k],lane);reference.set_register(&regs[k],v[k],lane);}}
            // per lane: list of (op index, description)
            let mut events:Vec<Vec<(usize,String)>>=vec![Vec::new();rows.len()];
            let mut seen=HashMap::<(&str,&str),Vec<bool>>::new();
            let mut stack=HashMap::<usize,Vec<(&str,Vec<[U256;2]>)>>::new();
            let mut entry=Vec::<[U256;2]>::new();let mut cursor=0;let mut unmatched_rev=0usize;
            sim.apply_observed(ops.iter(),|idx,s,_,_|{
                while cursor<marks.len()&&marks[cursor].at==idx{
                    let m=&marks[cursor];cursor+=1;
                    let vals:Vec<_>=(0..rows.len()).map(|lane|[word(&m.rails[0],&s.qubits,lane,p,m.low),word(&m.rails[1],&s.qubits,lane,p,m.low)]).collect();
                    match m.kind{
                        Kind::FwdBefore=>{entry=vals.clone();stack.entry(m.tick).or_default().push((m.phase,vals));}
                        Kind::RevBefore=>{}
                        Kind::FwdAfter=>{
                            let(ti,si)=(m.tick%2,1-m.tick%2);
                            let fs=seen.entry((m.phase,"fwd")).or_insert(vec![false;rows.len()]);
                            for lane in 0..rows.len(){
                                let tape:Vec<_>=m.letter.iter().map(|q|s.qubits[q.0 as usize]>>lane&1).collect();
                                if tape.len()<3||entry.is_empty(){continue;}
                                let mut want=entry[lane][ti];let source=entry[lane][si];
                                for &sign in &tape[..tape.len()-2]{want=half(if sign==0{want.add_mod(source,p)}else{sub(want,source,p)},p);}
                                for _ in 0..tape[tape.len()-2]+2*tape[tape.len()-1]{want=half(want,p);}
                                if (want!=vals[lane][ti]||source!=vals[lane][si])&&!fs[lane]{
                                    fs[lane]=true;
                                    let which=if source!=vals[lane][si]{"source"}else{"target"};
                                    let diff=sub(vals[lane][ti],want,p);
                                    let diff_s=sub(vals[lane][si],source,p);
                                    events[lane].push((m.at,format!("FWD_RAIL phase={} tick={} corrupt={which} widths={:?} tape={tape:?} diff_t={:#x} log2diff={} diff_s={:#x} got_t={:#x} want_t={:#x} got_s={:#x} want_s={:#x} low={}",m.phase,m.tick,[m.rails[0].len(),m.rails[1].len()],diff,diff.bit_len(),diff_s,vals[lane][ti],want,vals[lane][si],source,m.low)));
                                }
                            }
                            if Some(&m.tick)==last_tick.get(m.phase){
                                let es=seen.entry((m.phase,"end")).or_insert(vec![false;rows.len()]);
                                for lane in 0..rows.len(){
                                    let ok=vals[lane].iter().all(|v|*v==one||*v==p-one);
                                    if !ok&&!es[lane]{es[lane]=true;events[lane].push((m.at,format!("ENDPOINT phase={} tick={} rails={:#x},{:#x}",m.phase,m.tick,vals[lane][0],vals[lane][1])));}
                                }
                            }
                        }
                        Kind::RevAfter=>{
                            let rs=seen.entry((m.phase,"rev")).or_insert(vec![false;rows.len()]);
                            match stack.get_mut(&m.tick).and_then(|v|v.pop()){
                                None=>{unmatched_rev+=1;}
                                Some((fphase,before))=>{
                                    for lane in 0..rows.len(){
                                        if vals[lane]!=before[lane]&&!rs[lane]{
                                            rs[lane]=true;
                                            events[lane].push((m.at,format!("REV_RESTORE phase={} fwd_phase={fphase} tick={} widths={:?} got={:#x},{:#x} want={:#x},{:#x}",m.phase,m.tick,[m.rails[0].len(),m.rails[1].len()],vals[lane][0],vals[lane][1],before[lane][0],before[lane][1])));
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            });
            assert_eq!(cursor,marks.len());reference.apply_iter(ops.iter());
            assert_eq!(sim.qubits,reference.qubits);assert_eq!(sim.bits,reference.bits);assert_eq!(sim.phase,reference.phase);assert_eq!(sim.stats.toffoli_gates,reference.stats.toffoli_gates);
            for(lane,v)in rows.iter().enumerate(){
                let xb=sim.get_register(&regs[0],lane)!=v[4];let yb=sim.get_register(&regs[1],lane)!=v[5];
                let ev=&mut events[lane];ev.sort();
                let first=ev.first().map(|e|e.1.split_whitespace().next().unwrap().to_string()).unwrap_or_else(||"NONE".into());
                let first_phase=ev.first().map(|e|e.1.split_whitespace().nth(1).unwrap_or("").to_string()).unwrap_or_default();
                let cls=format!("final_bad={} first={first} {first_phase}",xb||yb);
                *summary.entry(cls).or_insert(0)+=1;
                eprintln!("TRACE family={family} shot={} final_bad={} x_bad={xb} y_bad={yb} events={}",batch*64+lane,xb||yb,ev.len());
                for (at,e) in ev.iter(){eprintln!("  EVENT family={family} shot={} at={at} {e}",batch*64+lane);}
            }
            if unmatched_rev>0{eprintln!("UNMATCHED_REV family={family} batch={batch} count={unmatched_rev}");}
        }
        let mut s:Vec<_>=summary.into_iter().collect();s.sort();
        eprintln!("TRACE_SUMMARY family={family} shots={} observer_equal=true score=NONE",points.len());
        for (k,v) in s{eprintln!("  CLASS family={family} {k} count={v}");}
    }
}
