use quantum_ecc::{circuit::{Op,OperationType as K,QubitId,BitId,RegisterId},sim::Simulator};
use alloy_primitives::U256;
use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
fn decode(bytes:&[u8])->Vec<Op>{bytes.chunks_exact(56).map(|r|{let f:Vec<u64>=r.chunks_exact(8).map(|x|u64::from_le_bytes(x.try_into().unwrap())).collect();let kind=match f[0]{0=>K::Neg,1=>K::Register,2=>K::AppendToRegister,3=>K::BitInvert,4=>K::BitStore0,5=>K::BitStore1,6=>K::X,7=>K::Z,8=>K::CX,9=>K::CZ,10=>K::Swap,11=>K::R,12=>K::Hmr,13=>K::CCX,14=>K::CCZ,15=>K::PushCondition,16=>K::PopCondition,17=>K::DebugPrint,_=>panic!()};let o=Op{kind,q_control2:QubitId(f[1]),q_control1:QubitId(f[2]),q_target:QubitId(f[3]),c_target:BitId(f[4]),c_condition:BitId(f[5]),r_target:RegisterId(f[6])};o.validate();o}).collect()}
fn next(x:&mut u64)->u64{*x^=*x<<13;*x^=*x>>7;*x^=*x<<17;*x}
fn get(q:&[u64],ids:&[usize],lane:usize)->U256{let mut v=U256::ZERO;for(i,id)in ids.iter().enumerate(){v.set_bit(i,q[*id]>>lane&1!=0);}v}
fn main(){
 let args:Vec<String>=std::env::args().collect();let data=std::fs::read(&args[1]).unwrap();assert_eq!(&data[..8],b"QVCARY01");let u=|at|u64::from_le_bytes(data[at..at+8].try_into().unwrap())as usize;assert_eq!(u(8),4);let mut at=16;
 let info:serde_json::Value=serde_json::from_slice(&std::fs::read(&args[2]).unwrap()).unwrap();let mut state=0x3ac413c0b1c6d;let mut cases=0;
 for row in info["rows"].as_array().unwrap(){let n=u(at);let m=u(at+8);at+=16;let old=decode(&data[at..at+56*n]);at+=56*n;let new=decode(&data[at..at+56*m]);at+=56*m;
  let ids=|name:&str|row[name].as_array().unwrap().iter().map(|x|x.as_u64().unwrap()as usize).collect::<Vec<_>>();let out=ids("out");let high=ids("high");let shift=row["shift"].as_u64().unwrap()as usize;let top=row["top"].as_u64().unwrap()as usize;let cin=row["carry_in"].as_u64().unwrap()as usize;let inv=row["inv"].as_bool().unwrap();
  assert!(!high.contains(&cin));assert!(high.iter().all(|q|!out.contains(q)));assert!(![row["previous"].as_u64().unwrap()as usize,row["penultimate"].as_u64().unwrap()as usize,row["top_bit"].as_u64().unwrap()as usize,row["next"].as_u64().unwrap()as usize].contains(&0));
  for case in 0u64..512{
   let mut iq=vec![0u64;1234];for q in out.iter().chain(high.iter()).chain(std::iter::once(&cin)){iq[*q]=next(&mut state);}let ib:Vec<u64>=(0..45701).map(|_|next(&mut state)).collect();let phase=next(&mut state);
   let mut h=Shake256::default();h.update(b"whole-square-window-independent-local-v1");h.update(&case.to_le_bytes());h.update(&(shift as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut rng2=rng.clone();let mut a=Simulator::new(1234,45701,&mut rng);let mut b=Simulator::new(1234,45701,&mut rng2);
   for s in [&mut a,&mut b]{s.qubits.copy_from_slice(&iq);s.bits.copy_from_slice(&ib);s.phase=phase;}
   a.apply_iter(old.iter());b.apply_iter(new.iter());assert_eq!(a.bits,b.bits,"every original classical bit");assert_eq!(a.phase,b.phase,"whole-window accumulated phase");assert_eq!(a.phase,phase,"valid-source arithmetic phase");
   for(oldmode,s)in [(true,&a),(false,&b)]{let w=top-shift+usize::from(!oldmode);let mask=(U256::from(1u64)<<w)-U256::from(1u64);let physical=mask<<shift;let mut eq=iq.clone();for lane in 0..64{let x=get(&iq,&out,lane);let v=get(&iq,&high,lane)+U256::from((iq[cin]>>lane)&1);let part=x>>shift;let sum=if inv{part.wrapping_sub(v)}else{part.wrapping_add(v)}&mask;let expected=(x&!physical)|(sum<<shift);for(i,q)in out.iter().enumerate(){eq[*q]=(eq[*q]&!(1u64<<lane))|((expected.bit(i)as u64)<<lane);}}assert_eq!(s.qubits,eq,"entire quantum interface/source arithmetic, all higher bits/donor/scratch");}
   cases+=64;
  }
 }
 assert_eq!(at,data.len());println!("{{\"status\":\"PASS\",\"complete_window_cases\":{cases},\"source_operands_arbitrary\":true,\"source_owned_carries_initial_zero\":true,\"classical_entry_arbitrary\":true,\"dirty_q0_restored\":true,\"all_quantum_and_classical_outputs_checked\":true,\"original_phase_preserved\":true,\"exact_original_w_and_repaired_w_plus1_integer_arithmetic\":true}}");
}
