
#[cfg(test)]mod phase_cubic_cap_tests{
 use super::*;use crate::circuit::{analyze_ops,Op,OperationType};use crate::sim::Simulator;use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 struct Words{data:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
 fn build(n:usize,pattern:usize,direct:bool)->(Vec<Op>,Vec<QubitId>,Vec<Lin>,Vec<crate::circuit::BitId>,crate::circuit::BitId,Vec<Vec<(usize,crate::circuit::BitId)>>){
  let mut c=Builder::new();let data=c.alloc_qubits(n);let k1=c.alloc_qubit();let k2=c.alloc_qubit();let bits=c.alloc_bits(n);let guard=c.alloc_bit();let all:Vec<_>=data.iter().copied().chain([k1,k2]).collect();c.declare_qubit_register(&all);
  let rows:Vec<_>=(0..n).map(|j|match pattern{0=>l(data[j]),1=>Lin::of(&[data[j],data[(j+1)%n]]),2=>l(data[j]).x(&if j%2==0{l(k1)}else{l(k2)}).x(&Lin::k(j%3==0)),_=>match j%4{0=>Lin::k(true),1=>l(k1),2=>l(k2),_=>Lin::of(&[data[j],k1,k2])}}).collect();
  let base=c.active_qubits();std::env::set_var("PEBBLE_HARD_CAP",if direct{base.to_string()}else{"1234".into()});c.push_condition(guard);let mut groups=Vec::new();let((),peak)=c.r3_peak(|c|{let mut p=T0Phase::new(c,k1,k2,n,bits.clone());assert_eq!(p.t.is_none(),direct);groups=p.at.clone();for j in 0..n{p.z(c,j,&rows[j]);}p.finish(c);});c.pop_condition();std::env::set_var("PEBBLE_HARD_CAP","1234");assert_eq!(peak,base+u32::from(!direct));(c.take_ops(),all,rows,bits,guard,groups)
 }
 fn fixture(n:usize,pattern:usize,guard_word:u64,probe:Option<usize>){
  let old=build(n,pattern,false);let new=build(n,pattern,true);assert_eq!(old.1,new.1);let(nq,nb,_,_)=analyze_ops(old.0.iter().chain(&new.0));let starts:Vec<_>=if probe.is_some(){vec![0x4AC0]}else{(0..1usize<<(2*n+2)).step_by(64).collect()};
  for start in starts{for(direct,item)in[(false,&old),(true,&new)]{let(ops,all,rows,bits,guard,groups)=item;let nr=draws(ops);let mut data=vec![0u8;nr*8];if let Some(p)=probe{for j in 0..nr{let word=if p==j||p==nr{u64::MAX}else{0};data[j*8..j*8+8].copy_from_slice(&word.to_le_bytes());}}else{let mut h=Shake256::default();h.update(b"phase-cubic-cap-measurements-v1");h.update(&(start as u64).to_le_bytes());h.finalize_xof().read(&mut data);}
   let mut rng=Words{data,pos:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);s.bits[guard.0 as usize]=guard_word;
   for lane in 0..64{let value=start+lane;for(i,&q)in all.iter().enumerate(){if value>>i&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}for(i,&bit)in bits.iter().enumerate(){if value>>(n+2+i)&1!=0{s.bits[bit.0 as usize]|=1u64<<lane;}}}let initial=s.qubits.clone();let initial_bits=s.bits.clone();let mut phase=0u64;
   for lane in 0..64{let e=(s.qubits[all[n].0 as usize]>>lane&1)+2*(s.qubits[all[n+1].0 as usize]>>lane&1);let mut p=0u64;for i in 0..n{let row=&rows[(i+e as usize)%n];let f=row.w.iter().fold(u64::from(row.one),|x,q|x^(s.qubits[q.0 as usize]>>lane&1));p^=(initial_bits[bits[i].0 as usize]>>lane&1)&f;}if p!=0&&guard_word>>lane&1!=0{phase|=1u64<<lane;}}
   let wanted_t=if !direct{guard_word.count_ones()as u64}else{let mut total=0u64;for j in 0..n{if rows[j].w.iter().any(|q|*q!=all[n]&&*q!=all[n+1]){let parity=groups[j].iter().filter(|(m,_)|*m==3).fold(0u64,|x,(_,bit)|x^initial_bits[bit.0 as usize]);total+=(parity&guard_word).count_ones()as u64;}}total};
   s.apply_iter(ops.iter());assert_eq!(s.qubits,initial);assert_eq!(s.phase,phase,"n={n} pattern={pattern} direct={direct} start={start}");assert_eq!(s.stats.toffoli_gates as u64,wanted_t);drop(s);assert_eq!(rng.pos,nr*8);
  }}
 }
 #[test]fn exact_rotated_linear_phase_without_clean_workspace_and_all_controls(){
  for n in 3usize..=7{for e in 0..4{assert_eq!(rot4_map(n,e),(0..n).map(|i|(i+e)%n).collect::<Vec<_>>());}for pattern in 0..4{for guard in[u64::MAX,0xA9563C78F012DE4B]{fixture(n,pattern,guard,None);}}}
  for pattern in 0..4{for guard in[0u64,u64::MAX,0xAA55AA55AA55AA55]{let old=build(9,pattern,false).0;for probe in 0..draws(&old)+2{fixture(9,pattern,guard,Some(probe));}}}
 }
}
