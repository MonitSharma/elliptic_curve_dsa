//! Finite exhaustive contract for retained-frame overflow cleanup.
use super::{Builder,modular,frame_kernel};
use crate::circuit::{analyze_ops,Op,OperationType as K};
use quantum_ecc::sim::Simulator;
use sha3::digest::XofReader;
struct Rng(u64);
impl XofReader for Rng {fn read(&mut self,b:&mut[u8]){assert_eq!(b.len(),8);self.0^=self.0<<13;self.0^=self.0>>7;self.0^=self.0<<17;b.copy_from_slice(&self.0.to_le_bytes());}}
fn circuit(n:usize)->Vec<Op>{
 let c=&mut Builder::new();let a=c.alloc_qubits(n);let b=c.alloc_qubits(n);let cin=c.alloc_qubit();let ov=c.alloc_qubit();let output=c.alloc_qubit();
 super::pingpong::with_phase_cap(Some(1267),||modular::ripple_add_consume(c,&a,&b,Some(cin),ov,|c,o,at,st,ct|{
  c.cx(o,output); // An external consumer may use the flag without changing its frame.
  modular::erase_overflow_from_frame(c,o,at,st,ct);
 }));c.take_ops()
}
#[test]
fn exhaustive_frame_consumer_all_measurements(){
 let(mut cases,mut proofs)=(0,0);
 for n in 1..=8 {let ops=circuit(n);let(nq,nb,_,_)=analyze_ops(ops.iter());let limit=1usize<<n;let total=2*limit*limit;
  for start in (0..total).step_by(64){let count=64.min(total-start);let mut input=vec![0u64;nq as usize];let mut want=vec![0u64;nq as usize];
   for lane in 0..count {let id=start+lane;let ci=id&1;let a=(id>>1)%limit;let b=(id>>(n+1))%limit;let dirty=(id^id.rotate_left(3))&1;let sum=a+b+ci;
    for j in 0..n{input[j]|=((a>>j&1)as u64)<<lane;input[n+j]|=((b>>j&1)as u64)<<lane;want[j]|=((a>>j&1)as u64)<<lane;want[n+j]|=((sum>>j&1)as u64)<<lane;}
    input[2*n]|=(ci as u64)<<lane;want[2*n]|=(ci as u64)<<lane;input[2*n+2]|=(dirty as u64)<<lane;want[2*n+2]|=((dirty^(sum>>n))as u64)<<lane;
   }
   let result=frame_kernel::audit(&ops,&input,&[]).unwrap();assert_eq!(result.qubits,want);let mut rng=Rng(0x123456789abcdef0^start as u64);let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);sim.qubits.clone_from(&input);sim.apply_iter(ops.iter());assert_eq!(sim.qubits,want);assert_eq!(sim.phase,0);cases+=count;proofs+=1;
  }
 }
 println!("TERMINAL_FRAME_CONTRACT exhaustive_integer_cases={cases} all_measurement_batch_proofs={proofs} native_agreement=true score=NONE");
}
#[test]
fn missing_top_phase_correction_is_detected(){
 let mut ops=circuit(3);let at=ops.iter().position(|o|o.kind==K::Z).expect("overflow frame has source-top Z");ops.remove(at);
 let(nq,_,_,_)=analyze_ops(ops.iter());let mut input=vec![0;nq as usize];input[2]=u64::MAX;
 assert!(frame_kernel::audit(&ops,&input,&[]).unwrap_err().starts_with("nonzero phase polynomial"));
}
