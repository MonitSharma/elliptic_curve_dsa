pub use quantum_ecc::{circuit,sim};
mod io;
mod proof;
use circuit::{Op,OperationType as K};
use sha3::{Digest,Sha3_256};
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let mut v=io::load_ops(&a[1]);let input=hash(&v);assert_eq!(input,a[3]);let old_t=v.iter().filter(|o|matches!(o.kind,K::CCX|K::CCZ)).count();let old_count=v.len();let tail=v.split_off(v.len()-96);for p in tail.chunks_exact(2){assert_eq!(p[0],p[1]);assert_eq!(p[0].kind,K::X);assert!(p[0].q_target.0<=1);assert_eq!(p[0].c_condition.0,u64::MAX);}let mut out=proof::run(v);out.extend(tail);let new_t=out.iter().filter(|o|matches!(o.kind,K::CCX|K::CCZ)).count();assert!(new_t<=old_t);let output=hash(&out);if input!=output{io::save_ops(&format!("{}.ops.bin",a[2]),&out);}
 let report=serde_json::json!({"status":"CURRENT_SOURCE_CLASSICAL_FACTOR_DIAGNOSTIC_NOT_A_SCORE","input_full_sha3_256":input,"output_full_sha3_256":output,"input_count":old_count,"output_count":out.len(),"original_static_Toffolis":old_t,"output_static_Toffolis":new_t,"static_Toffolis_removed":old_t-new_t,"complete_executed_mean_or_resource_score":null,"identity_tail_unchanged":true,"scope":"New source screen only. Old proxies and static deletion counts are not complete executed Toffolis or qualified records."});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&report).unwrap()).unwrap();println!("{}",report);
}
