//! Independent full-stream edit audit. No sampled assignments or nonce input.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId,BitId};
use sha3::{Digest,Sha3_256};
const NO:u64=u64::MAX;
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn fields(o:&Op)->[u64;7]{[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]}
fn main(){let r=std::path::PathBuf::from(std::env::args().nth(1).unwrap());let ws=r.parent().unwrap();
 let old=io::load_ops(ws.join("product-pareto-20261019/candidate-parent4/ops.bin").to_str().unwrap());
 let simple=io::load_ops(ws.join("product-classical-factors-refresh-20261019/parent4.ops.bin").to_str().unwrap());
 let nine=io::load_ops(ws.join("product-classical-nine-20261019/research.ops.bin").to_str().unwrap());
 assert_eq!(hash(&old),"97c40ed1dd3f5123c9554ebf29c54c433960804c0effce63dc7bba52844ae9ae");
 assert_eq!(hash(&simple),"f64a9d8c59cdc89e9b683988da84eb34fa78c5a884f0324ce824e4c07a00fa53");
 assert_eq!(hash(&nine),"4b81cbc1e247e791ab11ff56c5f84b4da5edc8618d7c19fe590305390fa6f93f");
 let rows:Vec<serde_json::Value>=serde_json::from_slice(&std::fs::read(r.join("AUDIT.json")).unwrap()).unwrap();assert_eq!(rows.len(),8);
 let(mut j,mut hit)=(0usize,0usize);
 for(i,o)in old.iter().enumerate(){
  if hit>=rows.len()||rows[hit]["source_index"].as_u64().unwrap()as usize!=i{assert_eq!(simple[j],*o,"outside factor replacement at {i}");j+=1;continue;}
  let row=&rows[hit];let expected:Vec<u64>=row["fields"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap()).collect();assert_eq!(fields(o).as_slice(),expected.as_slice());assert_eq!(o.kind,K::CCX);
  let other=row["other_wire"].as_u64().unwrap();let bit=row["bit"].as_u64().unwrap();assert!([o.q_control1.0,o.q_control2.0].contains(&other));
  let mut cx=Op::empty();cx.kind=K::CX;cx.q_control1=QubitId(other);cx.q_target=o.q_target;cx.c_condition=o.c_condition;
  if row["negated"]==true{assert_eq!(simple[j],cx);j+=1;}
  let mut push=Op::empty();push.kind=K::PushCondition;push.c_condition=BitId(bit);
  let mut pop=Op::empty();pop.kind=K::PopCondition;
  assert_eq!(&simple[j..j+3],&[push,cx,pop]);j+=3;hit+=1;
 }
 assert_eq!(j,simple.len());assert_eq!(hit,8);
 let index=5_387_927;assert_eq!(&simple[..index],&nine[..index]);assert_eq!(&simple[index+1..],&nine[index+2..]);
 assert_eq!(fields(&simple[index]),[13,706,816,703,NO,NO,NO]);
 for (offset,bit)in [773,774].into_iter().enumerate(){let mut x=Op::empty();x.kind=K::CX;x.q_control1=QubitId(816);x.q_target=QubitId(703);x.c_condition=BitId(bit);assert_eq!(nine[index+offset],x);}
 let events=|v:&[Op]|v.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).copied().collect::<Vec<_>>();assert_eq!(events(&old),events(&simple));assert_eq!(events(&old),events(&nine));
 let result=serde_json::json!({"status":"NINE_SOURCE_BOUND_REPLACEMENTS_AND_ALL_OTHER_OPS_VERIFIED","factor_replacements":8,"classical_XOR_replacements":1,"all_outside_ops_identical":true,"all_R_Hmr_fields_and_event_order_identical":true,"all_original_classical_writes_identical":true,"no_new_qubits_or_classical_bits":true,"raw_sha3_256":hash(&nine),"scope":"Full stream edit and RNG-transcript transfer audit; no nonce filter acceptance or resource score."});
 std::fs::write(r.join("EDIT-AUDIT.json"),serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("{}",result);
}
