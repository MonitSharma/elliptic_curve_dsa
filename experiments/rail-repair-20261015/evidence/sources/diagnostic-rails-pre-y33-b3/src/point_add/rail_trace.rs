//! Observation-only checks of exact forward rail maps on preserved inputs.
use crate::circuit::{analyze_ops, Op, QubitId};
use alloy_primitives::U256;
use sha3::{Shake256,digest::{Update,ExtendableOutput}};
use std::{collections::HashMap,sync::Mutex};
#[derive(Clone)]
struct Mark { at:usize, phase:&'static str, tick:usize, after:bool, rails:[Vec<QubitId>;2], letter:Vec<QubitId>, low:bool }
static MARKS:Mutex<Vec<Mark>>=Mutex::new(Vec::new());
pub fn mark(at:usize,phase:&'static str,tick:usize,after:bool,rails:&[Vec<QubitId>;2],letter:&[QubitId],low:bool){
    MARKS.lock().unwrap().push(Mark{at,phase,tick,after,rails:rails.clone(),letter:letter.to_vec(),low});
}
fn sub(a:U256,b:U256,p:U256)->U256{if a>=b{a-b}else{p-(b-a)}}
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
    let root="/home/hclau/ecdsa_research/arithmetic-repair-20261015";
    let(nq,nb,_,regs)=analyze_ops(ops.iter());let p=super::SECP256K1_P;
    let marks=MARKS.lock().unwrap().clone();
    for family in ["independent","structured","candidate"]{
        let text=std::fs::read_to_string(format!("{root}/packets/{family}.tsv")).unwrap();
        let points:Vec<[U256;6]>=text.lines().map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
        let(mut rail_bad,mut final_bad)=(0,0);
        for(batch,rows)in points.chunks(64).enumerate(){
            let mut h=Shake256::default();h.update(b"arithmetic-repair-stage-v1");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut ref_rng=rng.clone();
            let mut sim=super::observed_sim::Simulator::new(nq as usize,nb as usize,&mut rng);
            let mut reference=crate::sim::Simulator::new(nq as usize,nb as usize,&mut ref_rng);
            for(lane,v)in rows.iter().enumerate(){for k in 0..4{sim.set_register(&regs[k],v[k],lane);reference.set_register(&regs[k],v[k],lane);}}
            let mut first=HashMap::<&str,Vec<bool>>::new();let mut entry=Vec::<[U256;2]>::new();let mut entry_at=0;let mut cursor=0;
            sim.apply_observed(ops.iter(),|idx,s,_,_|{
                while cursor<marks.len()&&marks[cursor].at==idx{
                    let m=&marks[cursor];cursor+=1;
                    let vals:Vec<_>=(0..rows.len()).map(|lane|[word(&m.rails[0],&s.qubits,lane,p,m.low),word(&m.rails[1],&s.qubits,lane,p,m.low)]).collect();
                    if !m.after{entry=vals;entry_at=m.at;continue;}
                    assert!(!entry.is_empty());let(ti,si)=(m.tick%2,1-m.tick%2);
                    let seen=first.entry(m.phase).or_insert(vec![false;rows.len()]);
                    for lane in 0..rows.len(){
                        let tape:Vec<_>=m.letter.iter().map(|q|s.qubits[q.0 as usize]>>lane&1).collect();assert!(tape.len()>=3);
                        let mut want=entry[lane][ti];let source=entry[lane][si];
                        for &sign in &tape[..tape.len()-2]{want=half(if sign==0{want.add_mod(source,p)}else{sub(want,source,p)},p);}
                        for _ in 0..tape[tape.len()-2]+2*tape[tape.len()-1]{want=half(want,p);}
                        if (want!=vals[lane][ti]||source!=vals[lane][si])&&!seen[lane]{
                            seen[lane]=true;rail_bad+=1;
                            eprintln!("FIRST_RAIL_BAD family={family} shot={} phase={} tick={} start={} end={} tape={tape:?} before_t={:#x} before_s={source:#x} expected_t={want:#x} got_t={:#x} got_s={:#x} widths={:?}",batch*64+lane,m.phase,m.tick,entry_at,m.at,entry[lane][ti],vals[lane][ti],vals[lane][si],[m.rails[0].len(),m.rails[1].len()]);
                        }
                    }
                }
            });
            assert_eq!(cursor,marks.len());reference.apply_iter(ops.iter());
            assert_eq!(sim.qubits,reference.qubits);assert_eq!(sim.bits,reference.bits);assert_eq!(sim.phase,reference.phase);assert_eq!(sim.stats.toffoli_gates,reference.stats.toffoli_gates);
            for(lane,v)in rows.iter().enumerate(){if sim.get_register(&regs[0],lane)!=v[4]||sim.get_register(&regs[1],lane)!=v[5]{final_bad+=1;}}
        }
        eprintln!("RAIL_SUMMARY family={family} shots={} first_rail_failures={rail_bad} final_bad={final_bad} observer_equal=true score=NONE",points.len());
    }
}
