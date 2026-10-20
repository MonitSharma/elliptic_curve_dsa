
#[cfg(test)]mod exact_strip_port_tests{
 use super::*;use crate::sim::Simulator;use sha3::digest::XofReader;
 struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
 #[test]fn exact_strip_signed_all_inputs_phase_garbage_inverse_and_fault(){
  let mut checked=0u64;let mut faults=0u64;std::env::remove_var("LF_STRIP");
  for w in(4usize..=18).chain([25,26,31,32,63,64]){let mask=if w==64{u64::MAX}else{(1u64<<w)-1};let total=if w<=16{1usize<<w}else{4096};for inverse in[false,true]{for garbage in[false,true]{if !sb_avail(w,inverse,garbage){continue;}for combo in 0..if garbage{4}else{1}{
   let mut c=Builder::new();let ks=c.alloc_qubits(2);let t=c.alloc_qubits(w);let aux=c.alloc_qubits(2);let dropped=strip_barrel(&mut c,ks[0],ks[1],&t,inverse,garbage.then_some((aux[0],aux[1])));assert_eq!(dropped,!inverse);let(nq,nb)=c.i13_dims();let ops=c.take_ops();let faulty:Vec<_>=ops.iter().filter(|o|!matches!(o.kind,crate::circuit::OperationType::CZ|crate::circuit::OperationType::Z)).copied().collect();
   for begin in(0..total).step_by(64){for pattern in[0u8,255,0xa5,0x5a]{let mut rng=Fixed(pattern);let mut frng=Fixed(pattern);let mut s=Simulator::new(nq,nb,&mut rng);let mut f=Simulator::new(nq,nb,&mut frng);let mut expected=vec![0u64;nq];
    for lane in 0..64{let index=(begin+lane)as u64;let mut x=if w<=16{index}else{index.wrapping_mul(0x9e3779b97f4a7c15).rotate_left((index%63)as u32)}&mask;if x&15==0{x^=1;}let k2=u64::from(x&3==0);let k1=u64::from(x&1==0)^(k2*((x>>2)&1));let e=(k1+2*k2)as usize;let sign=x>>(w-1)&1;let y=if e==0{x}else{(x>>e)|if sign==1{mask^(mask>>e)}else{0}};assert_eq!(y&1,1);let ell=((combo&1)^((combo>>1)&1))as u64;let garbage_x=if garbage&&e>0{x.wrapping_sub(2*ell)&mask}else{x};let input=if inverse{y}else{garbage_x};let output=if inverse{garbage_x}else{y};
     for i in 0..w{s.qubits[t[i].0 as usize]|=((input>>i)&1)<<lane;expected[t[i].0 as usize]|=((if !inverse&&i==0{0}else{output>>i&1}))<<lane;}
     for(i,value)in[k1,k2].into_iter().enumerate(){s.qubits[ks[i].0 as usize]|=value<<lane;expected[ks[i].0 as usize]|=value<<lane;}
     for i in 0..2{let value=(combo>>i&1)as u64;s.qubits[aux[i].0 as usize]|=value<<lane;expected[aux[i].0 as usize]|=value<<lane;}
    }
    f.qubits.clone_from(&s.qubits);s.apply_iter(ops.iter());f.apply_iter(faulty.iter());assert_eq!(s.qubits,expected,"w={w} inverse={inverse} garbage={garbage} combo={combo} begin={begin} pattern={pattern}");assert_eq!(s.phase,0,"strip phase w={w} inverse={inverse} garbage={garbage} combo={combo} begin={begin} pattern={pattern}");faults+=u64::from(f.phase!=0);checked+=64;
   }}
  }}}}assert!(faults>0,"Missing phase repair must be detected");eprintln!("EXACT_STRIP_NATIVE checked={checked} phase_fault_batches={faults} exhaustive_widths=4..16 sampled_widths=17,18,25,26,31,32,63,64");
 }
}
