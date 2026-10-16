use quantum_ecc::{circuit::{Op,OperationType as K,QubitId,BitId},sim::Simulator};
use sha3::digest::XofReader;
struct Words{v:[u64;6],at:usize}
impl XofReader for Words{fn read(&mut self,out:&mut[u8]){assert_eq!(out.len(),8);out.copy_from_slice(&self.v[self.at].to_le_bytes());self.at+=1;}}
fn next(v:&mut u64)->u64{*v^=*v<<13;*v^=*v>>7;*v^=*v<<17;*v}
fn main(){
 let root="/home/hclau/ecdsa_research/current-value-attribution-20261016";
 let data:serde_json::Value=serde_json::from_slice(&std::fs::read(format!("{root}/tick131-first-add-ops.json")).unwrap()).unwrap();
 let qids=[256,257,258,259,764,699,852,853,554,555,556,553];let mut bmap=std::collections::BTreeMap::new();
 for row in data["first80"].as_array().unwrap().iter().take(31){let f=row["fields"].as_array().unwrap();if f[0].as_u64().unwrap()==12{let n=bmap.len()+2;bmap.entry(f[4].as_u64().unwrap()).or_insert(n);}}
 assert_eq!(bmap.len(),1,"actual source reuses one classical HMR slot");let mut ops=Vec::new();for b in [0,1]{let mut o=Op::empty();o.kind=K::PushCondition;o.c_condition=BitId(b);ops.push(o);}let mut inv=Op::empty();inv.kind=K::BitInvert;inv.c_target=BitId(0);ops.push(inv);
 for row in data["first80"].as_array().unwrap().iter().take(31){let f:Vec<_>=row["fields"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap()).collect();let mut o=Op::empty();o.kind=match f[0]{8=>K::CX,9=>K::CZ,11=>K::R,12=>K::Hmr,13=>K::CCX,_=>panic!()};let q=|id|QubitId(qids.iter().position(|x|*x==id).unwrap()as u64);if f[1]!=u64::MAX{o.q_control2=q(f[1]);}if f[2]!=u64::MAX{o.q_control1=q(f[2]);}o.q_target=q(f[3]);if f[4]!=u64::MAX{o.c_target=BitId(bmap[&f[4]]as u64);}if f[5]!=u64::MAX{o.c_condition=BitId(bmap[&f[5]]as u64);}o.validate();ops.push(o);}
 for _ in 0..2{let mut o=Op::empty();o.kind=K::PopCondition;ops.push(o);}let mut cases=0;let mut st=0x4a86414dc9b7;let mut negative=0;
 for input in 0..4096{for mode in 0..4{
  let mut iq=vec![0u64;13];for i in 0..12{iq[i]=if input>>i&1==0{0}else{u64::MAX};}iq[12]=next(&mut st);
  let mut ib:Vec<u64>=(0..6).map(|_|next(&mut st)).collect();if mode==0{ib[0]=0;}if mode==1{ib[0]=u64::MAX;ib[1]=u64::MAX;}let g=ib[0]&ib[1];let phase=next(&mut st);let words=std::array::from_fn(|_|next(&mut st));let mut rng=Words{v:words,at:0};let mut sim=Simulator::new(13,6,&mut rng);sim.qubits.copy_from_slice(&iq);sim.bits.copy_from_slice(&ib);sim.phase=phase;
  sim.apply_iter(ops.iter());let mut eq=iq.clone();let mut eb=ib.clone();eb[0]^=g;let mut ci=0;
  for i in 0..4{let(a,b)=(iq[i],iq[4+i]);let sum=a^b^ci;eq[4+i]=(b&!g)|(sum&g);ci=iq[8+i]^(a&b)^(a&ci)^(b&ci);}
  for i in 0..3{eq[8+i]&=!g;}eq[11]=(iq[11]&!g)|(ci&g);let mut ep=phase;
  for(j,i)in [2,1,0].into_iter().enumerate(){let w=words[2*j];ep^=g&w&iq[8+i];eb[2]=(eb[2]&!g)|(w&g);}
  assert_eq!(sim.qubits,eq,"ALL quantum outputs, dirty carries, unrelated frame");assert_eq!(sim.bits,eb,"ALL original classical outputs, Push snapshots");assert_eq!(sim.phase,ep,"exact dirty-residual phase polynomial");if ep!=phase{negative+=1;}drop(sim);assert_eq!(rng.at,6,"every HMR/R including inactive");cases+=64;
 }}
 assert!(negative>0);println!("{{\"status\":\"PASS\",\"protected_cases\":{cases},\"all12_entry_quantum_assignments\":true,\"arbitrary_mixed_MR_and_classical_guards\":true,\"all_q_b_phase_draws_checked\":true,\"false_clean_phase_negative_cases\":{negative}}}");
}
