pub use quantum_ecc::circuit;
use circuit::{Op,OperationType as K,QubitId,BitId,RegisterId};
use std::{io::Read,collections::BTreeSet};
mod support;
fn load(path:&str)->Vec<Op>{
 let mut f=std::fs::File::open(path).unwrap();let mut h=[0u8;16];f.read_exact(&mut h).unwrap();assert_eq!(&h[..8],b"QECCOPSZ");let n=u64::from_le_bytes(h[8..].try_into().unwrap())as usize;
 let mut d=zstd::stream::read::Decoder::new(f).unwrap();let mut ops=Vec::with_capacity(n);let mut rec=[0u8;56];
 for _ in 0..n{d.read_exact(&mut rec).unwrap();let f:Vec<u64>=rec.chunks_exact(8).map(|x|u64::from_le_bytes(x.try_into().unwrap())).collect();
  let kind=match f[0]{0=>K::Neg,1=>K::Register,2=>K::AppendToRegister,3=>K::BitInvert,4=>K::BitStore0,5=>K::BitStore1,6=>K::X,7=>K::Z,8=>K::CX,9=>K::CZ,10=>K::Swap,11=>K::R,12=>K::Hmr,13=>K::CCX,14=>K::CCZ,15=>K::PushCondition,16=>K::PopCondition,17=>K::DebugPrint,_=>panic!()};
  let o=Op{kind,q_control2:QubitId(f[1]),q_control1:QubitId(f[2]),q_target:QubitId(f[3]),c_target:BitId(f[4]),c_condition:BitId(f[5]),r_target:RegisterId(f[6])};o.validate();ops.push(o);
 }let mut end=[0u8;1];assert_eq!(d.read(&mut end).unwrap(),0);ops
}
fn main(){
 let args:Vec<String>=std::env::args().collect();assert_eq!(args.len(),3);let ops=load(&args[1]);let qs:BTreeSet<usize>=std::fs::read_to_string(&args[2]).unwrap().lines().map(|x|x.parse().unwrap()).collect();let mut left=qs.len();let mut s=support::Support::new(&ops);let start=std::time::Instant::now();
 for(at,o)in ops.iter().enumerate(){
  if qs.contains(&at){println!("{}",serde_json::json!({"at":at,"zeros":s.zero_ids(),"seconds":start.elapsed().as_secs_f64()}));left-=1;}
  if left==0{break}let _=s.step(o);
 }
 assert_eq!(left,0);eprintln!("ALL_QUERIES_PASS seconds={}",start.elapsed().as_secs_f64());
}
