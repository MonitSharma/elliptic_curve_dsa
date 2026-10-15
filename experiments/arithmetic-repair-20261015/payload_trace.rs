//! Checks a mathematical relation; does not change operations or score anything.
use crate::circuit::{analyze_ops, Op, QubitId};
use alloy_primitives::U256;
use sha3::{Shake256, digest::{Update, ExtendableOutput}};
use std::{collections::HashMap, sync::Mutex};
#[derive(Clone)]
struct Check { at:usize, kind:&'static str, tick:usize, rails:[Vec<QubitId>;2], pay:Option<[Vec<QubitId>;2]>, low:bool }
static CHECKS:Mutex<Vec<Check>>=Mutex::new(Vec::new());
pub fn mark(at:usize,kind:&'static str,tick:usize,r:&[Vec<QubitId>;2],p:Option<&[Vec<QubitId>;2]>,low:bool){
    CHECKS.lock().unwrap().push(Check{at,kind,tick,rails:r.clone(),pay:p.cloned(),low});
}
fn sub(a:U256,b:U256,p:U256)->U256{if a>=b{a-b}else{p-(b-a)}}
fn word(qs:&[QubitId],words:&[u64],lane:usize,p:U256,signed:bool,low:bool)->U256{
    assert!(qs.len()<=260);let f=U256::from(0x1000003d1u64);let mut v=U256::ZERO;
    for(i,q)in qs.iter().enumerate(){if words[q.0 as usize]>>lane&1!=0{if i<256{v|=U256::from(1)<<i;}else{v=v.add_mod(f<<(i-256),p);}}}
    if v>=p{v-=p;}
    if signed&&words[qs.last().unwrap().0 as usize]>>lane&1!=0{
        let pow=if qs.len()<256{U256::from(1)<<qs.len()}else{f<<(qs.len()-256)};v=sub(v,pow,p);
    }
    if low{v=v.add_mod(v,p).add_mod(U256::from(1),p);}v
}
pub fn run(ops:&[Op]){
    let root="/home/hclau/ecdsa_research/arithmetic-repair-20261015";
    let(nq,nb,_,regs)=analyze_ops(ops.iter());let p=super::SECP256K1_P;
    let checks=CHECKS.lock().unwrap().clone();
    for family in ["independent","structured","candidate"]{
        let text=std::fs::read_to_string(format!("{root}/packets/{family}.tsv")).unwrap();
        let points:Vec<[U256;6]>=text.lines().map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
        let mut failures=0;
        for(batch,rows)in points.chunks(64).enumerate(){
            let mut h=Shake256::default();h.update(b"arithmetic-repair-stage-v1");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();
            let mut sim=super::observed_sim::Simulator::new(nq as usize,nb as usize,&mut rng);
            for(lane,v)in rows.iter().enumerate(){for k in 0..4{sim.set_register(&regs[k],v[k],lane);}}
            let slope:Vec<_>=rows.iter().map(|v|sub(v[1],v[3],p).mul_mod(sub(v[0],v[2],p).pow_mod(p-U256::from(2),p),p)).collect();
            let mut stored=HashMap::<usize,Vec<[U256;2]>>::new();let mut first=vec![false;rows.len()];let mut cursor=0;
            sim.apply_observed(ops.iter(),|idx,s,_,_|{
                while cursor<checks.len()&&checks[cursor].at==idx{
                    let ch=&checks[cursor];cursor+=1;
                    if ch.kind=="rail"{
                        let rv:Vec<_>=(0..rows.len()).map(|lane|[word(&ch.rails[0],&s.qubits,lane,p,true,ch.low),word(&ch.rails[1],&s.qubits,lane,p,true,ch.low)]).collect();stored.insert(ch.tick,rv);
                    }
                    if let Some(pay)=&ch.pay{
                        let rails=stored.get(&ch.tick).expect("payload must have prior rails");
                        for lane in 0..rows.len(){
                            for k in 0..2{
                                let got=word(&pay[k],&s.qubits,lane,p,false,false);let expected=slope[lane].mul_mod(rails[lane][k],p);
                                if got!=expected&&!first[lane]{first[lane]=true;failures+=1;eprintln!("FIRST_INVARIANT_BAD family={family} shot={} kind={} tick={} payload={k} op={} got={got:#x} expected={expected:#x} rail={:#x}",batch*64+lane,ch.kind,ch.tick,ch.at,rails[lane][k]);}
                            }
                        }
                    }
                }
            });
            assert_eq!(cursor,checks.len());
        }
        eprintln!("PAYLOAD_DIAGNOSTIC family={family} shots={} invariant_bad_shots={failures} score=NONE",points.len());
    }
}
