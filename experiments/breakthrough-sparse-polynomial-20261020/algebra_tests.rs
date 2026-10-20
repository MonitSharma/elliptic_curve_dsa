fn empty()->Support{Support{qubits:vec![],bits:vec![],base_condition:Affine::constant(true),condition_stack:vec![],next_atom:0,products:std::collections::HashMap::new()}}
fn eval(p:&Affine,r:usize)->bool{p.atoms.iter().fold(p.constant,|v,m|v^m.iter().all(|&a|r>>(a as usize)&1!=0))}
#[test]fn sparse_boolean_ring_matches_independent_scalar_values(){
 let mut s=empty();let xs:Vec<_>=(0..8).map(|_|s.fresh()).collect();let make=|c,mut terms:Vec<Vec<u64>>|{for m in &mut terms{m.sort_unstable();m.dedup();}terms.sort();Affine{constant:c,atoms:terms}};
 for i in 0..120{let a=make(i%3==0,vec![vec![(i%8)as u64],vec![((i+1)%8)as u64,((i+3)%8)as u64]]);let b=make(i%5==0,vec![vec![((i+2)%8)as u64],vec![((i+4)%8)as u64,((i+6)%8)as u64]]);let x=s.xor(&a,&b);let y=s.and(&a,&b);for r in 0..256{assert_eq!(eval(&x,r),eval(&a,r)^eval(&b,r));assert_eq!(eval(&y,r),eval(&a,r)&eval(&b,r));}}
 let a=s.and(&xs[0],&xs[1]);let b=s.and(&xs[0],&xs[2]);let lhs=s.xor(&a,&b);let sum=s.xor(&xs[1],&xs[2]);let rhs=s.and(&xs[0],&sum);assert!(lhs==rhs);assert!(s.and(&lhs,&lhs)==lhs);
}
#[test]fn overflow_is_immutable_and_operation_tagged(){
 let mut s=empty();let xs:Vec<_>=(0..40).map(|_|s.fresh()).collect();let a=Affine{constant:false,atoms:xs.iter().take(32).flat_map(|p|p.atoms.clone()).collect()};let b=xs[32].clone();let x=s.xor(&a,&b);let y=s.and(&a,&b);assert!(x!=y);assert!(s.xor(&a,&b)==x);assert!(s.and(&a,&b)==y);s.products.clear();let z=s.xor(&a,&b);assert!(x!=z);assert!(!x.is_zero()&&!x.is_one());
 let long=Affine{constant:false,atoms:vec![(0..33).collect()]};let v=s.and(&long,&xs[34]);assert_eq!(v.atoms[0].len(),1);
}
