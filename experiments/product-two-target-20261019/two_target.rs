mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId};
use std::collections::{HashMap,VecDeque};
use sha3::{Digest,Sha3_256};
const NO:u64=u64::MAX;
#[derive(Clone,Debug)]struct Pair{first:usize,second:usize,a:u64,b:u64,d:u64,e:u64,flag:u64}
fn dims(v:&[Op])->(usize,usize){(v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1,v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1)}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn find(v:&[Op],gap:usize)->Vec<Pair>{let(nq,nb)=dims(v);let mut touch=vec![None;nq];let mut write=vec![None;nq];let mut cwrite=vec![None;nb];let mut used=vec![false;v.len()];let mut candidates:HashMap<(u64,u64,u64),VecDeque<usize>>=HashMap::new();let(mut depth,mut fence)=(0usize,None);let mut pairs=vec![];
 for(i,o)in v.iter().enumerate(){if matches!(o.kind,K::Register|K::AppendToRegister|K::DebugPrint){fence=Some(i);}
  if o.kind==K::CCX&&depth==0{let(a,b)=(o.q_control1.0.min(o.q_control2.0),o.q_control1.0.max(o.q_control2.0));let(e,flag)=(o.q_target.0,o.c_condition.0);let key=(a,b,flag);let old=candidates.entry(key).or_default();while old.front().is_some_and(|&j|i-j>gap){old.pop_front();}let mut selected=None;
   for &j in old.iter().rev(){if used[j]{continue;}let d=v[j].q_target.0;if d==e||[a,b].contains(&d)||[a,b].contains(&e){continue;}let before=|x:Option<usize>|x.is_none_or(|x|x<=j);if before(fence)&&before(write[a as usize])&&before(write[b as usize])&&(flag==NO||before(cwrite[flag as usize]))&&touch[d as usize]==Some(j)&&before(touch[e as usize]){selected=Some((j,d));break;}}
   if let Some((j,d))=selected{used[j]=true;used[i]=true;pairs.push(Pair{first:j,second:i,a,b,d,e,flag});}else{old.push_back(i);}
  }
  for q in [o.q_control1.0,o.q_control2.0,o.q_target.0]{if q!=NO{touch[q as usize]=Some(i);}}
  if matches!(o.kind,K::X|K::CX|K::CCX|K::R|K::Hmr|K::Swap){write[o.q_target.0 as usize]=Some(i);if o.kind==K::Swap{write[o.q_control1.0 as usize]=Some(i);}}
  if matches!(o.kind,K::Hmr|K::BitInvert|K::BitStore0|K::BitStore1){cwrite[o.c_target.0 as usize]=Some(i);}
  if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth=depth.checked_sub(1).unwrap();}
 }assert_eq!(depth,0);pairs
}
fn emit(p:&Pair)->[Op;3]{let mut cx=Op::empty();cx.kind=K::CX;cx.q_control1=QubitId(p.d);cx.q_target=QubitId(p.e);cx.c_condition=quantum_ecc::circuit::BitId(p.flag);let mut cc=Op::empty();cc.kind=K::CCX;cc.q_control1=QubitId(p.a);cc.q_control2=QubitId(p.b);cc.q_target=QubitId(p.d);cc.c_condition=cx.c_condition;for o in [cx,cc]{o.validate();}[cx,cc,cx]}
fn rewrite(v:&[Op],pairs:&[Pair])->Vec<Op>{let mut starts=HashMap::new();let mut removed=std::collections::HashSet::new();for p in pairs{assert!(starts.insert(p.first,p).is_none());assert!(removed.insert(p.second));}assert!(starts.keys().all(|i|!removed.contains(i)));let mut out=Vec::with_capacity(v.len()+pairs.len());for(i,o)in v.iter().enumerate(){if let Some(p)=starts.get(&i){out.extend(emit(p));}else if !removed.contains(&i){out.push(*o);}}out}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),5);let v=io::load_ops(&a[1]);let input=hash(&v);assert_eq!(input,a[4]);let gap=a[3].parse().unwrap();assert!([1,64,4096].contains(&gap));let pairs=find(&v,gap);let mut output=None;if !pairs.is_empty(){let out=rewrite(&v,&pairs);io::save_ops(&format!("{}.ops.bin",a[2]),&out);output=Some(hash(&out));}let report=serde_json::json!({"status":"EXACT_TWO_DIRTY_TARGET_SOURCE_QUERY_NOT_A_SCORE","input_full_sha3_256":input,"input_count":v.len(),"max_original_operation_gap":gap,"pair_count":pairs.len(),"unconditional_pairs":pairs.iter().filter(|p|p.flag==NO).count(),"output_full_sha3_256":output,"no_extra_quantum_or_classical_bits":true,"all_R_and_Hmr_order_preserved":true,"pairs":pairs.iter().map(|p|serde_json::json!({"first":p.first,"second":p.second,"a":p.a,"b":p.b,"d":p.d,"e":p.e,"flag":p.flag})).collect::<Vec<_>>(),"scope":"Pair count is a source diagnostic; complete executed savings, native reproduction, census and benchmark remain required."});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&report).unwrap()).unwrap();println!("gap={gap} pairs={}",pairs.len());}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::{circuit::{BitId,RegisterId},sim::Simulator};use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 fn op(k:K,q:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_target=QubitId(q);o}
 fn fixture()->Vec<Op>{let mut v=vec![];for q in 0..5{let mut o=op(K::AppendToRegister,q);o.r_target=RegisterId(0);v.push(o);}let mut c=op(K::AppendToRegister,NO);c.c_target=BitId(0);c.r_target=RegisterId(1);v.push(c);for q in [2,3]{let mut o=op(K::CCX,q);o.q_control1=QubitId(0);o.q_control2=QubitId(1);o.c_condition=BitId(0);v.push(o);}v}
 fn run(v:&[Op],bits:u64,flag:u64)->(Vec<u64>,Vec<u64>,u64,u64,[u8;64]){let mut h=Shake256::default();Update::update(&mut h,b"two-target-control");let mut rng=h.finalize_xof();let mut s=Simulator::new(5,1,&mut rng);for q in 0..5{s.qubits[q]=if bits>>q&1!=0{u64::MAX}else{0};}s.bits[0]=flag;s.phase=0x5555aaaaffff0000;s.apply_iter(v.iter());let state=(s.qubits.clone(),s.bits.clone(),s.phase,s.stats.toffoli_gates);drop(s);let mut t=[0;64];rng.read(&mut t);(state.0,state.1,state.2,state.3,t)}
 #[test]fn dirty_target_identity_all_basis_values_flags_and_phase(){for body in [vec![],vec![op(K::X,4)],vec![op(K::Z,0)]]{let mut v=fixture();v.splice(7..7,body);let p=find(&v,64);assert_eq!(p.len(),1);let w=rewrite(&v,&p);for bits in 0..32{for f in [0,u64::MAX,0x5555aaaaffff0000]{let x=run(&v,bits,f);let y=run(&w,bits,f);assert_eq!(x.0,y.0);assert_eq!(x.1,y.1);assert_eq!(x.2,y.2);assert_eq!(x.4,y.4);assert_eq!(x.3-y.3,f.count_ones()as u64);}}}}
 #[test]fn target_read_blocks_moving_the_second_toggle(){let mut v=fixture();v.insert(7,op(K::Z,3));assert!(find(&v,64).is_empty());}
 #[test]fn dirty_donor_read_blocks_its_encoding(){let mut v=fixture();v.insert(7,op(K::Z,2));assert!(find(&v,64).is_empty());}
 #[test]fn control_write_blocks_pair(){let mut v=fixture();v.insert(7,op(K::X,0));assert!(find(&v,64).is_empty());}
 #[test]fn direct_guard_write_blocks_pair(){let mut v=fixture();let mut b=op(K::BitInvert,NO);b.c_target=BitId(0);v.insert(7,b);assert!(find(&v,64).is_empty());}
 #[test]fn original_gap_limit_is_enforced(){let mut v=fixture();v.insert(7,op(K::X,4));assert!(find(&v,1).is_empty());assert_eq!(find(&v,64).len(),1);}
 #[test]fn metadata_fence_blocks_pair(){let mut v=fixture();v.insert(7,op(K::DebugPrint,NO));assert!(find(&v,64).is_empty());}
 #[test]fn different_direct_conditions_do_not_pair(){let mut v=fixture();v[7].c_condition=BitId(NO);assert!(find(&v,64).is_empty());}
 #[test]fn consumed_pair_is_not_reused(){let mut v=fixture();v.push(v[6]);assert_eq!(find(&v,64).len(),1);}
}
