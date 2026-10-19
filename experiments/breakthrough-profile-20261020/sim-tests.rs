
#[cfg(test)] mod regional_tests {
 use super::*;
 fn op(k:u8,a:u16,b:u16,t:u16,c:u32,bt:u32)->CompactOp{CompactOp{a,b,t,k,pad:0,c,bt}}
 #[test] fn counters_preserve_guard_stack_measurements_phase_and_rng(){
  let z=u32::MAX;
  let ops=vec![op(13,0,1,2,z,z),op(15,0,0,0,0,z),op(13,0,1,2,z,z),op(16,0,0,0,z,z),
   op(12,0,0,2,z,1),op(13,0,1,2,1,z),op(14,0,1,2,0,z),op(11,0,0,2,z,z)];
  let ends=[0usize,2,4,7,8];let mut q=vec![0u64;24];let mut b=vec![0u64;16];
  for j in 0..8{q[j]=0xAAAA5555AAAA5555u64.rotate_left(j as u32);q[8+j]=0x3333CCCC3333CCCCu64.rotate_left(j as u32);b[j]=0xF0F00F0FF0F00F0Fu64.rotate_left(j as u32);}
  let mut rq=q.clone();let mut rb=b.clone();let rng:Vec<_>=(0..16).map(|j|0x123456789ABCDEF0u64.rotate_left(j)).collect();
  let(mut p,mut rp,mut t,mut rt,mut used,mut ru)=([0u64;8],[0u64;8],[0u64;8],[0u64;8],0usize,0usize);
  let mut stack=vec![0u64;64];let mut rstack=stack.clone();let mut profile=vec![0u64;40];
  assert_eq!(unsafe{simd8_profile(ops.as_ptr(),ops.len(),q.as_mut_ptr(),b.as_mut_ptr(),p.as_mut_ptr(),rng.as_ptr(),2,stack.as_mut_ptr(),8,&mut used,t.as_mut_ptr(),ends.as_ptr(),ends.len(),profile.as_mut_ptr())},0);
  assert_eq!(unsafe{simd8_run(ops.as_ptr(),ops.len(),rq.as_mut_ptr(),rb.as_mut_ptr(),rp.as_mut_ptr(),rng.as_ptr(),2,rstack.as_mut_ptr(),8,&mut ru,rt.as_mut_ptr())},0);
  assert_eq!(q,rq);assert_eq!(b,rb);assert_eq!(p,rp);assert_eq!(t,rt);assert_eq!(used,ru);assert_eq!(used,2);
  for j in 0..8{assert_eq!(profile[j],0);assert_eq!(profile[8+j],64);assert_eq!(profile[16+j],32);assert_eq!(profile[24+j],rng[j].count_ones()as u64+32);assert_eq!(profile[32+j],0);assert_eq!((0..5).map(|r|profile[r*8+j]).sum::<u64>(),t[j]);}
 }
}
