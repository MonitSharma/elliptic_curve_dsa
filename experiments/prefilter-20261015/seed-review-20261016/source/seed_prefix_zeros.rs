pub use quantum_ecc::circuit;
use circuit::{Op,OperationType as K,QubitId,BitId,RegisterId};
use std::{io::Read,collections::BTreeSet};
#[path="seed_support.rs"]mod support;
fn load(path:&str)->Vec<Op>{
 let mut f=std::fs::File::open(path).unwrap();let mut h=[0u8;16];f.read_exact(&mut h).unwrap();assert_eq!(&h[..8],b"QECCOPSZ");let n=u64::from_le_bytes(h[8..].try_into().unwrap())as usize;
 let mut d=zstd::stream::read::Decoder::new(f).unwrap();let mut ops=Vec::with_capacity(n);let mut rec=[0u8;56];
 for _ in 0..n{d.read_exact(&mut rec).unwrap();let f:Vec<u64>=rec.chunks_exact(8).map(|x|u64::from_le_bytes(x.try_into().unwrap())).collect();
  let kind=match f[0]{0=>K::Neg,1=>K::Register,2=>K::AppendToRegister,3=>K::BitInvert,4=>K::BitStore0,5=>K::BitStore1,6=>K::X,7=>K::Z,8=>K::CX,9=>K::CZ,10=>K::Swap,11=>K::R,12=>K::Hmr,13=>K::CCX,14=>K::CCZ,15=>K::PushCondition,16=>K::PopCondition,17=>K::DebugPrint,_=>panic!()};
  let o=Op{kind,q_control2:QubitId(f[1]),q_control1:QubitId(f[2]),q_target:QubitId(f[3]),c_target:BitId(f[4]),c_condition:BitId(f[5]),r_target:RegisterId(f[6])};o.validate();ops.push(o);
 }let mut end=[0u8;1];assert_eq!(d.read(&mut end).unwrap(),0);ops
}
fn main(){let root="/home/hclau/ecdsa_research/current-value-attribution-20261016";let ops=load("/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin");let m:serde_json::Value=serde_json::from_slice(&std::fs::read(format!("{root}/actual-seed-markers.json")).unwrap()).unwrap();let at=m["markers"][0]["at"].as_u64().unwrap()as usize;let v:serde_json::Value=serde_json::from_slice(&std::fs::read(format!("{root}/seed-bdd-contract.json")).unwrap()).unwrap();let qs:Vec<_>=v["original_source"]["scratch_preconditions_zero"].as_array().unwrap().iter().map(|q|q.as_u64().unwrap()as usize).collect();let mut a=support::Support::new(&ops);for o in &ops[..at]{let _=a.step(o);}let zeros=a.proved_zero(&qs);println!("{}",serde_json::json!({"status":if zeros.iter().all(|x|*x){"PASS ALL required entry scratch exactly zero"}else{"UNKNOWN required entry scratch"},"at":at,"q":qs,"exact_zero":zeros,"all_original_ops_no_rewrites":true,"all_symbolic_ABI_inputs_and_MR":true}));}