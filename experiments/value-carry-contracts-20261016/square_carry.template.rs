//! Frozen complete four-window C130 precision family. All inherited passes
//! and their original assertions run before this exact full-input guard.
use crate::circuit::{Op,OperationType as K,QubitId,BitId,RegisterId,analyze_ops};
use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
const NONE:u64=u64::MAX;
const DATA:&[u8]=include_bytes!("square_carry.bin");
const EXPECTED_INPUT:[u8;32]=@INPUT_DIGEST@;
const INPUT_OPS:usize=@INPUT_OPS@;
#[derive(Clone,Copy)]struct Meta{at:usize,p:u64,a:u64,t:u64,u:u64,d:u64,shift:usize}
const META:[Meta;4]=[@META@];
fn decode(bytes:&[u8])->Vec<Op>{assert_eq!(bytes.len()%56,0);bytes.chunks_exact(56).map(|r|{let f:Vec<u64>=r.chunks_exact(8).map(|x|u64::from_le_bytes(x.try_into().unwrap())).collect();let kind=match f[0]{0=>K::Neg,1=>K::Register,2=>K::AppendToRegister,3=>K::BitInvert,4=>K::BitStore0,5=>K::BitStore1,6=>K::X,7=>K::Z,8=>K::CX,9=>K::CZ,10=>K::Swap,11=>K::R,12=>K::Hmr,13=>K::CCX,14=>K::CCZ,15=>K::PushCondition,16=>K::PopCondition,17=>K::DebugPrint,_=>panic!("unknown op")};let o=Op{kind,q_control2:QubitId(f[1]),q_control1:QubitId(f[2]),q_target:QubitId(f[3]),c_target:BitId(f[4]),c_condition:BitId(f[5]),r_target:RegisterId(f[6])};o.validate();o}).collect()}
fn digest(ops:&[Op])->[u8;32]{let mut h=Shake256::default();for o in ops{for v in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(&v.to_le_bytes());}}let mut out=[0u8;32];h.finalize_xof().read(&mut out);out}
fn ccx(a:u64,b:u64,t:u64)->Op{assert!(a!=b&&a!=t&&b!=t);let mut o=Op::empty();o.kind=K::CCX;o.q_control2=QubitId(a);o.q_control1=QubitId(b);o.q_target=QubitId(t);o}
fn quantum(ops:&[Op])->std::collections::BTreeSet<u64>{ops.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|q|*q!=NONE).collect()}
fn contract(old:&[Op],new:&[Op],m:Meta){
 assert_eq!(new.len(),old.len()+4);assert_eq!(old[m.at],ccx(m.p,m.a,m.t));
 let used=quantum(old);assert!(!used.contains(&m.u),"nextU read/write/phase in entire old window");
 let ids:std::collections::BTreeSet<_>=[m.p,m.a,m.t,m.u,m.d].into_iter().collect();assert_eq!(ids.len(),5,"dirty donor/control alias");assert!(ids.iter().all(|q|*q<1234));
 assert_eq!(&new[..m.at],&old[..m.at]);assert_eq!(&new[m.at+5..],&old[m.at+1..]);
 assert_eq!(&new[m.at..m.at+5],&[ccx(m.p,m.a,m.d),ccx(m.d,m.t,m.u),ccx(m.p,m.a,m.d),ccx(m.d,m.t,m.u),old[m.at]]);
 let mut depth=0isize;for o in old{if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth-=1;}assert!(depth>=0);}assert_eq!(depth,0);
 let classical=|x:&[Op]|x.iter().filter(|o|matches!(o.kind,K::R|K::Hmr|K::BitInvert|K::BitStore0|K::BitStore1|K::PushCondition|K::PopCondition|K::Register|K::AppendToRegister)).copied().collect::<Vec<_>>();assert_eq!(classical(old),classical(new),"all MR, bits, scopes, ABI unchanged");
}
fn specs()->Vec<(Vec<Op>,Vec<Op>)>{assert_eq!(&DATA[..8],b"QVCARY01");let u=|at|u64::from_le_bytes(DATA[at..at+8].try_into().unwrap())as usize;assert_eq!(u(8),4);let mut at=16;let mut out=Vec::new();for _ in 0..4{let n=u(at);let m=u(at+8);at+=16;let old=decode(&DATA[at..at+56*n]);at+=56*n;let new=decode(&DATA[at..at+56*m]);at+=56*m;out.push((old,new));}assert_eq!(at,DATA.len());out}
fn positions(ops:&[Op],old:&[Op])->Vec<usize>{ops.windows(old.len()).enumerate().filter_map(|(i,w)|(w==old).then_some(i)).collect()}
pub fn run(ops:Vec<Op>)->Vec<Op>{
 assert_eq!(ops.len(),INPUT_OPS,"frozen source input length");assert_eq!(digest(&ops),EXPECTED_INPUT,"frozen full pre-tail source digest");
 let(nq,nb,_,regs)=analyze_ops(ops.iter());assert_eq!((nq,nb),(1234,45701));
 let mut found=Vec::new();for(j,(old,new))in specs().into_iter().enumerate(){contract(&old,&new,META[j]);let hit=positions(&ops,&old);assert_eq!(hit.len(),1,"entire C130 window missing/edited/ambiguous");found.push((hit[0],old,new));eprintln!("VALUE_CARRY_SQUARE shift={} at={} addedT=4 addedQ=0 addedMR=0 dirty_donor={}",META[j].shift,hit[0],META[j].d);}
 found.sort_by_key(|x|x.0);for pair in found.windows(2){assert!(pair[0].0+pair[0].1.len()<=pair[1].0);}
 let starts:std::collections::BTreeSet<_>=found.iter().map(|x|x.0).collect();let mut depth=0isize;for(at,o)in ops.iter().enumerate(){if starts.contains(&at){assert_eq!(depth,0,"whole old window scope boundary");}if o.kind==K::PushCondition{depth+=1}if o.kind==K::PopCondition{depth-=1}assert!(depth>=0);}assert_eq!(depth,0);
 let mut out=Vec::with_capacity(ops.len()+16);let mut cursor=0;for(at,old,new)in found{out.extend_from_slice(&ops[cursor..at]);out.extend_from_slice(&new);cursor=at+old.len();}out.extend_from_slice(&ops[cursor..]);let(nq2,nb2,_,regs2)=analyze_ops(out.iter());assert_eq!((nq2,nb2),(nq,nb));assert_eq!(regs,regs2);out
}
#[cfg(test)]mod tests{use super::*;
 #[test]fn all_four_contracts(){for(j,(a,b))in specs().iter().enumerate(){contract(a,b,META[j]);}}
 #[test]fn ambiguity_rejected(){let(a,_)=specs().remove(0);let mut x=a.clone();x.extend_from_slice(&a);assert_eq!(positions(&x,&a).len(),2);}
 #[test]#[should_panic]fn donor_alias_rejected(){let(a,b)=specs().remove(0);let mut m=META[0];m.d=m.u;contract(&a,&b,m);}
 #[test]#[should_panic]fn next_read_rejected(){let(mut a,b)=specs().remove(0);a[0].q_target=QubitId(META[0].u);contract(&a,&b,META[0]);}
 #[test]#[should_panic]fn changed_mr_rejected(){let(a,mut b)=specs().remove(0);let i=b.iter().position(|o|o.kind==K::Hmr).unwrap();b[i].c_target=BitId(45699);contract(&a,&b,META[0]);}
 #[test]#[should_panic]fn wrong_cubic_rejected(){let(a,mut b)=specs().remove(0);b[META[0].at+1].q_control1=QubitId(META[0].a);contract(&a,&b,META[0]);}
 #[test]fn changed_whole_input_digest_detected(){let(a,_)=specs().remove(0);let mut b=a.clone();b[0].kind=K::Neg;assert_ne!(digest(&a),digest(&b));}
}
