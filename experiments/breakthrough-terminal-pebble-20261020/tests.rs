
#[cfg(test)]mod terminal_contract_tests{
 use super::*;use crate::circuit::{analyze_ops,Op,OperationType};use crate::sim::Simulator;use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 struct Words{data:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
 fn circuit(n:usize,k:usize,has_cin:bool,desired:bool,drops:Option<&[usize]>)->(Vec<Op>,Vec<QubitId>,u32){
  let mut c=Builder::new();let a=c.alloc_qubits(n);let b=c.alloc_qubits(n);let ci=c.alloc_qubit();let guard=c.alloc_bit();assert_eq!(guard.0,0);
  let interface:Vec<_>=a.iter().chain(&b).copied().chain([ci]).collect();c.declare_qubit_register(&interface);let before=c.active_qubits();
  c.push_condition(guard);let((),peak)=c.r3_peak(|c|{
   if let Some(ds)=drops{let rows:Vec<_>=(0..n).map(|i|if i<k{vec![a[i]]}else{vec![]}).collect();assert!(crate::point_add::terminal_pebble::apply(c,&b,&rows,&vec![false;n],has_cin.then_some(ci),ds,desired));}
   else{ripple_add_proved(c,&a[..k],&b,has_cin.then_some(ci),None,Carry0::Full,Carry1::Full,None,None,Some(desired),None);}
  });c.pop_condition();let want=n-2-drops.map_or(0,|d|d.len());assert_eq!(peak,before+want as u32);(c.take_ops(),interface,peak)
 }
 fn fixture(n:usize,k:usize,has_cin:bool,desired:bool,drops:&[usize],guard:u64,probe:Option<usize>){
  let(old,interface,_)=circuit(n,k,has_cin,desired,None);let(new,interface2,_)=circuit(n,k,has_cin,desired,Some(drops));assert_eq!(interface,interface2);
  let m=n-2;assert_eq!(draws(&old),2*m+1);assert_eq!(draws(&new),m+1);
  let shifted:Vec<_>=drops.iter().map(|&i|i+usize::from(!has_cin)).collect();
  let mut order=shifted.clone();order.push(0);order.extend((1..=m).rev().filter(|i|!shifted.contains(i)));assert_eq!(order.len(),m+1);
  let nq=analyze_ops(old.iter().chain(&new)).0 as usize;let nb=analyze_ops(old.iter().chain(&new)).1 as usize;
  let starts:Vec<_>=if probe.is_some(){vec![0x4C380]}else{(0..1usize<<(2*n+1)).step_by(64).collect()};
  for start in starts{
   let mut h=Shake256::default();h.update(b"terminal-pebble-channel-words-v1");h.update(&(start as u64).to_le_bytes());let mut hash=h.finalize_xof();let mut bytes=vec![0u8;(2*m+1)*8];hash.read(&mut bytes);
   let oldwords:Vec<u64>=if let Some(p)=probe{(0..2*m+1).map(|i|if p==i||p==2*m+1{u64::MAX}else{0}).collect()}else{bytes.chunks(8).map(|b|u64::from_le_bytes(b.try_into().unwrap())).collect()};
   let newwords:Vec<_>=order.iter().map(|&i|oldwords[if i==0{0}else{1+2*(m-i)}]).collect();
   let mut oldrng=Words{data:oldwords.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0};let mut newrng=Words{data:newwords.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0};
   let mut a=Simulator::new(nq,nb,&mut oldrng);let mut b=Simulator::new(nq,nb,&mut newrng);a.bits[0]=guard;b.bits[0]=guard;
   for lane in 0..64{for(i,&q)in interface.iter().enumerate(){if(start+lane)>>i&1!=0{a.qubits[q.0 as usize]|=1u64<<lane;b.qubits[q.0 as usize]|=1u64<<lane;}}}let original=a.qubits.clone();
   a.apply_iter(old.iter());b.apply_iter(new.iter());assert_eq!(a.qubits,b.qubits,"n={n} k={k} cin={has_cin} desired={desired} drops={drops:?} start={start}");assert_eq!(a.phase,b.phase,"channel phase n={n} k={k} cin={has_cin} desired={desired} drops={drops:?} start={start}");
   for lane in 0..64{let value=start+lane;let av=value&((1<<k)-1);let bv=value>>n&((1<<n)-1);let ci=if has_cin{value>>(2*n)&1}else{0};let wanted=if guard>>lane&1==0{bv}else{((av+bv+ci)&((1<<(n-1))-1))|usize::from(desired)<<(n-1)};
    for i in 0..n{assert_eq!(b.qubits[interface[n+i].0 as usize]>>lane&1,(wanted>>i&1)as u64);}}
   for i in 0..nq{if !interface[n..2*n].iter().any(|q|q.0 as usize==i){assert_eq!(b.qubits[i],original[i]);}}
   assert_eq!(a.stats.toffoli_gates as u64,m as u64*guard.count_ones()as u64);drop(a);drop(b);assert_eq!(oldrng.pos,(2*m+1)*8);assert_eq!(newrng.pos,(m+1)*8);
  }
 }
 #[test]fn all_small_inputs_include_violated_promises_padding_and_guards(){for n in 5usize..=7{for has_cin in[false,true]{let m=n-2-usize::from(!has_cin);for mask in 0usize..1usize<<(m-1){let ds:Vec<_>=(1..m).filter(|&i|mask>>(i-1)&1!=0).collect();let room=m-ds.len();if ds.iter().enumerate().any(|(j,&i)|i+1-j>room||j>0&&ds[j-1]+1>=i){continue;}for k in[1,n-2,n-1,n]{for desired in[false,true]{for guard in[u64::MAX,0xA9563C78F012DE4B]{fixture(n,k,has_cin,desired,&ds,guard,None);}}}}}}}
 #[test]fn every_original_measurement_and_reset_word_has_semantic_alignment(){for has_cin in[false,true]{for ds in[vec![1],vec![2],vec![1,3],vec![2,4]]{for k in[1,6,7,8]{for desired in[false,true]{for probe in 0..15{for guard in[0u64,u64::MAX,0xAA55AA55AA55AA55]{fixture(8,k,has_cin,desired,&ds,guard,Some(probe));}}}}}}}
 #[test]fn invalid_alias_contract_rejects_before_emission(){let mut c=Builder::new();let a=c.alloc_qubits(7);let b=c.alloc_qubits(7);let ci=c.alloc_qubit();let mut rows:Vec<_>=a.iter().map(|&q|vec![q]).collect();let before=c.op_count();rows[2]=vec![b[1]];assert!(!crate::point_add::terminal_pebble::apply(&mut c,&b,&rows,&[false;7],Some(ci),&[1],false));assert!(!crate::point_add::terminal_pebble::apply(&mut c,&b,&rows,&[false;7],None,&[1],false));assert_eq!(before,c.op_count());}
}
