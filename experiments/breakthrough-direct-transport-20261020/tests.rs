
#[cfg(test)]mod direct_transport_tests{
 use super::*;use crate::circuit::{analyze_ops,Op,OperationType};use crate::sim::Simulator;use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 struct Words{data:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
 fn build(n:usize,pattern:usize,mode:usize,adapt:bool)->(Vec<Op>,Vec<QubitId>,Vec<Vec<QubitId>>){
  let mut c=Builder::new();let a=c.alloc_qubits(n);let b=c.alloc_qubits(n);let ci=c.alloc_qubit();let shared=c.alloc_qubit();let guard=c.alloc_bit();assert_eq!(guard.0,0);
  let interface:Vec<_>=a.iter().chain(&b).copied().chain([ci,shared]).collect();c.declare_qubit_register(&interface);
  let rows:Vec<_>=(0..n).map(|i|match pattern{0=>vec![a[i]],1=>if i%2==0{vec![a[i],shared]}else{vec![a[i]]},2=>vec![shared],_=>if i%3==1{vec![]}else{vec![a[i]]}}).collect();
  let w=n/2;let plan=Plan{sizes:vec![w,w],slow:false,extra2:w-1,peak:w};let base=c.active_qubits();
  std::env::set_var("PEBBLE_HARD_CAP",if adapt{(base as usize+w-1).to_string()}else{"1234".into()});
  c.push_condition(guard);let((),peak)=c.r3_peak(|c|match mode{
   3=>{let held=direct_add_hold(c,&rows,&b,ci,&plan);c.x_all(&b);direct_add_unhold(c,&rows,&b,ci,&plan,held);c.x_all(&b);},
   4=>{let(held,kept)=direct_add_hold_keep(c,&rows,&b,ci,&plan,1);c.x_all(&b);direct_add_unhold_keep(c,&rows,&b,ci,&plan,held,kept);c.x_all(&b);},
   _=>{let pending=direct_add_phase_transport(c,&rows,&b,ci,&plan,mode==2||mode==5,&[]);if mode!=0{c.x_all(&b);assert!(direct_add_phase_transport(c,&rows,&b,ci,&plan,false,if mode==2{&pending}else{&[]}).is_empty());c.x_all(&b);}}
  });c.pop_condition();std::env::set_var("PEBBLE_HARD_CAP","1234");
  let wanted=if adapt&&mode!=4{w-1}else{w};assert_eq!(peak,base+wanted as u32,"n={n} pattern={pattern} mode={mode} adapt={adapt}");
  (c.take_ops(),interface,rows)
 }
 fn fixture(n:usize,pattern:usize,mode:usize,guard:u64,probe:Option<usize>){
  let(old,interface,rows)=build(n,pattern,mode,false);let(new,interface2,_)=build(n,pattern,mode,true);assert_eq!(interface,interface2);
  let(nq,nb,_,_)=analyze_ops(old.iter().chain(&new));let starts:Vec<_>=if mode==5{vec![15usize<<n]}else if probe.is_some(){vec![0x36D80]}else{(0..1usize<<(2*n+2)).step_by(64).collect()};
  for start in starts{for ops in[&old,&new]{let nr=draws(ops);let mut bytes=vec![0u8;nr*8];if let Some(p)=probe{for i in 0..nr{let word=if p==usize::MAX||p==i||p==nr{u64::MAX}else{0};bytes[i*8..i*8+8].copy_from_slice(&word.to_le_bytes());}}else{let mut h=Shake256::default();h.update(b"direct-transport-measurements-v1");h.update(&(start as u64).to_le_bytes());h.finalize_xof().read(&mut bytes);}
   let mut rng=Words{data:bytes,pos:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);s.bits[0]=guard;
   for lane in 0..64{for(i,&q)in interface.iter().enumerate(){if(start+lane)>>i&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}}let original=s.qubits.clone();s.apply_iter(ops.iter());
   for lane in 0..64{let v=start+lane;let mut av=0usize;for(i,row)in rows.iter().enumerate(){let x=row.iter().fold(0usize,|x,q|x^(v>>interface.iter().position(|r|r==q).unwrap()&1));av|=x<<i;}
    let bv=v>>n&((1<<n)-1);let ci=v>>(2*n)&1;let expected=if mode==0&&guard>>lane&1!=0{(av+bv+ci)&((1<<n)-1)}else{bv};for i in 0..n{assert_eq!(s.qubits[interface[n+i].0 as usize]>>lane&1,(expected>>i&1)as u64,"n={n} pattern={pattern} mode={mode}");}}
   for i in 0..nq as usize{if !interface[n..2*n].iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}
   if mode==5{assert_ne!(s.phase,0,"deliberate omitted recover must be detected");}else{assert_eq!(s.phase,0,"n={n} pattern={pattern} mode={mode} start={start}");}drop(s);assert_eq!(rng.pos,nr*8);
  }}
 }
 #[test]fn exact_direct_maps_deferred_recovery_and_held_boundaries_with_lower_peak(){
  // One test owns all environment changes; other filters run in separate processes.
  for pattern in 0..4{for mode in 0..4{for guard in[u64::MAX,0xA9563C78F012DE4B]{fixture(8,pattern,mode,guard,None);}}}
  for pattern in 0..4{for mode in 0..5{let old=build(12,pattern,mode,false).0;let new=build(12,pattern,mode,true).0;let nr=draws(&old).max(draws(&new));for probe in 0..nr+2{for guard in[0u64,u64::MAX,0xAA55AA55AA55AA55]{fixture(12,pattern,mode,guard,Some(probe));}}}}
  fixture(8,0,5,u64::MAX,Some(usize::MAX));
 }
}
