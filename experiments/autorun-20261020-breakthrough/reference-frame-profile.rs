// Read-only projection. No rewritten circuit or scored counts are produced.
// q = B XOR delta: B is a classical reference, D encloses delta's support.
fn product_domain(e:&mut Expr,da:u32,db:u32,ba:u32,bb:u32)->u32 {
 let ab=e.and(da,db);let ax=e.and(da,bb);let bx=e.and(db,ba);
 let v=e.or(ab,ax);e.or(v,bx)
}
fn reference_profile(ops:&[Op])->serde_json::Value {
 let no=u64::MAX;let(nq,nb,_,_)=quantum_ecc::circuit::analyze_ops(ops.iter());
 let(nq,nb)=(nq as usize,nb as usize);let mut alg=Algebra{inner:Expr::default()};
 let(mut q,mut c)=initial_inputs(ops,nq,nb,&mut alg);let mut bv=vec![0;nq];
 let pinned:HashSet<usize>=ops.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=no).map(|o|o.q_target.0 as usize).collect();
 let mut d:Vec<u32>=(0..nq).map(|i|u32::from(pinned.contains(&i))).collect();
 let(mut base,mut stack)=(1,vec![]);let(mut peak,mut peak_at)=(pinned.len(),0);
 let(mut ccx,mut removed_ccx,mut ccz,mut removed_ccz,mut classical_helper_uses,mut resets_classical)=(0u64,0u64,0u64,0u64,0u64,0u64);
 let mut curve=vec![];let mut removed=vec![];
 for(i,o)in ops.iter().enumerate(){
  if o.kind==K::PushCondition{stack.push(base);base=alg.inner.and(base,c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=stack.pop().expect("balanced conditions");continue;}
  let g=if o.c_condition.0==no{base}else{alg.inner.and(base,c[o.c_condition.0 as usize])};
  let(t,a,b,ct)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize,o.c_target.0 as usize);
  let used:Vec<_>=[o.q_control2.0,o.q_control1.0,o.q_target.0].into_iter().filter(|&q|q!=no).map(|q|q as usize).collect();
  classical_helper_uses+=used.iter().filter(|&&j|!pinned.contains(&j)&&d[j]==0&&bv[j]!=0).count()as u64;
  match o.kind {
   K::X=>{q[t]=alg.inner.xor(q[t],g);bv[t]=alg.inner.xor(bv[t],g);},
   K::CX=>{let v=alg.inner.and(q[a],g);q[t]=alg.inner.xor(q[t],v);let v=alg.inner.and(bv[a],g);bv[t]=alg.inner.xor(bv[t],v);let v=alg.inner.and(d[a],g);d[t]=alg.inner.or(d[t],v);},
   K::CCX=>{
    ccx+=1;let ab=alg.inner.and(d[a],d[b]);let nonlinear=alg.inner.and(g,ab);if nonlinear==0{removed_ccx+=1;if removed.len()<64{removed.push(i);}}
    let domain=product_domain(&mut alg.inner,d[a],d[b],bv[a],bv[b]);let domain=alg.inner.and(g,domain);d[t]=alg.inner.or(d[t],domain);
    let v=alg.inner.and(q[a],q[b]);let v=alg.inner.and(g,v);q[t]=alg.inner.xor(q[t],v);
    let v=alg.inner.and(bv[a],bv[b]);let v=alg.inner.and(g,v);bv[t]=alg.inner.xor(bv[t],v);
   },
   K::CCZ=>{ccz+=1;let v=alg.inner.and(d[a],d[b]);let v=alg.inner.and(v,d[t]);if alg.inner.and(v,g)==0{removed_ccz+=1;if removed.len()<64{removed.push(i);}}},
   K::Swap=>{let v=alg.inner.xor(q[a],q[t]);let v=alg.inner.and(g,v);q[a]=alg.inner.xor(q[a],v);q[t]=alg.inner.xor(q[t],v);let v=alg.inner.xor(bv[a],bv[t]);let v=alg.inner.and(g,v);bv[a]=alg.inner.xor(bv[a],v);bv[t]=alg.inner.xor(bv[t],v);let(da,dt)=(d[a],d[t]);d[a]=alg.inner.ite(g,dt,da);d[t]=alg.inner.ite(g,da,dt);},
   K::R|K::Hmr=>{
    if d[t]==0 {resets_classical+=1;let live=pinned.len()+(0..nq).filter(|j|!pinned.contains(j)&&d[*j]!=0).count();let scratch=usize::from(!pinned.iter().any(|&j|d[j]==0));if live+scratch>peak{peak=live+scratch;peak_at=i;}}
    q[t]=alg.inner.and(q[t],g^1);bv[t]=alg.inner.and(bv[t],g^1);d[t]=alg.inner.and(d[t],g^1);
    if o.kind==K::Hmr{let r=alg.inner.atom();c[ct]=alg.inner.ite(g,r,c[ct]);}
   },
   K::BitInvert=>c[ct]=alg.inner.xor(c[ct],g),K::BitStore0=>c[ct]=alg.inner.and(c[ct],g^1),K::BitStore1=>c[ct]=alg.inner.or(c[ct],g),
   K::Neg|K::Z|K::CZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},_=>unreachable!()
  }
  // Exact original-state equality strengthens, never weakens, the support proof.
  for &j in &used{if q[j]==bv[j]{d[j]=0;}}
  let live=pinned.len()+(0..nq).filter(|j|!pinned.contains(j)&&d[*j]!=0).count();if live>peak{peak=live;peak_at=i;}
  if i%1000000==0{eprintln!("REFERENCE_PROFILE op={i} projected_peak={peak} live={live} nodes={} removable_ccx={removed_ccx} removable_ccz={removed_ccz}",alg.inner.nodes.len());curve.push(serde_json::json!([i,peak,live,alg.inner.nodes.len()]));}
 }
 assert!(stack.is_empty());serde_json::json!({"status":"READ_ONLY_CLASSICAL_REFERENCE_FRAME_PROJECTION_NOT_A_CIRCUIT_OR_SCORE","original_qubits":nq,"pinned_qubits":pinned.len(),"projected_peak_slots_including_rng_scratch":peak,"peak_at_operation":peak_at,"ccx_records":ccx,"ccz_records":ccz,"nonlinear_ccx_terms_proven_zero":removed_ccx,"nonlinear_ccz_terms_proven_zero":removed_ccz,"first_removed_nonlinear_record_indices":removed,"classical_nonzero_helper_uses":classical_helper_uses,"classical_delta_zero_resets":resets_classical,"semantic_nodes":alg.inner.nodes.len(),"progress":curve,"input_records_sha3":hash(ops),"scope":"No emitted circuit, no executed count, no candidate/gate/nonce/benchmark. Projection counts only nonclassical deviation helper lifetimes with registered inputs pinned. Exact phase/guard/RNG-preserving emission and independent full protected qualification remain required."})
}

#[cfg(test)]mod frame_domain_tests {
 use super::*;
 #[test]fn product_deviation_domain_exhaustive(){for bits in 0..256u32{let ba=bits&1;let bb=(bits>>1)&1;let da=(bits>>2)&1;let db=(bits>>3)&1;let xa=(bits>>4)&1;let xb=(bits>>5)&1;let g=(bits>>6)&1;let old=(bits>>7)&1;if xa>da||xb>db{continue;}let mut e=Expr::default();let domain=product_domain(&mut e,da,db,ba,bb);let flip=((ba^xa)&(bb^xb))^(ba&bb);assert_eq!(flip&!domain,0);let new=old|(g&domain);assert_eq!((g&flip)&!new,0);}}
 #[test]fn phase_expansion_exhaustive(){for bits in 0..128u32{let a=bits&1;let b=(bits>>1)&1;let c=(bits>>2)&1;let x=(bits>>3)&1;let y=(bits>>4)&1;let z=(bits>>5)&1;let g=(bits>>6)&1;let expanded=(x&y&z)^(a&y&z)^(b&x&z)^(c&x&y)^(a&b&z)^(a&c&y)^(b&c&x)^(a&b&c);assert_eq!(g&((a^x)&(b^y)&(c^z)),g&expanded);assert_eq!(g&((a^x)&(b^y)),g&((x&y)^(a&y)^(b&x)^(a&b)));}}
 #[test]fn classical_basis_helper_can_remove_a_quantum_nonlinear_term(){let n=u64::MAX;let mut ops=vec![];for(q,r)in[(0,0),(1,1)]{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=quantum_ecc::circuit::RegisterId(r);if q==0{o.q_target=QubitId(0);}else{o.c_target=BitId(0);}ops.push(o);}ops.extend([make(K::X,n,n,1,n,0),make(K::CCX,0,1,2,n,n),make(K::R,n,n,2,n,0)]);let s=reference_profile(&ops);assert_eq!(s["original_qubits"],3);assert_eq!(s["projected_peak_slots_including_rng_scratch"],2);assert_eq!(s["nonlinear_ccx_terms_proven_zero"],1);}
}
