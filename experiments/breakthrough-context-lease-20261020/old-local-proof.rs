fn local_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool{if last-first>200000{return false;}
 let no=u64::MAX;let mut alg=Algebra{next:1,products:HashMap::new(),cap:65536,truncations:0};
 let mut q:Vec<E>=(0..nq).map(|_|alg.fresh()).collect();let mut c:Vec<E>=(0..nb).map(|_|alg.fresh()).collect();
 let f=ops[first];let product=alg.and(&q[f.q_control1.0 as usize],&q[f.q_control2.0 as usize]);let expected=if f.c_condition.0==no{product}else{alg.and(&product,&c[f.c_condition.0 as usize])};
 let mut base=vec![0];let mut stack=vec![];
 for o in &ops[first..last]{
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=match stack.pop(){Some(x)=>x,None=>return false};continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};if eff.is_empty(){continue;}
  match o.kind{
   K::X=>q[t]=alg.xor(&q[t],&eff),
   K::CX=>{let v=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&v);},
   K::CCX=>{let v=alg.and(&q[a],&q[b]);let v=alg.and(&v,&eff);q[t]=alg.xor(&q[t],&v);},
   K::Swap=>{let v=alg.xor(&q[a],&q[t]);let v=alg.and(&v,&eff);q[a]=alg.xor(&q[a],&v);q[t]=alg.xor(&q[t],&v);},
   K::R|K::Hmr=>{q[t]=alg.select(&q[t],&vec![],&eff);if o.kind==K::Hmr{let v=alg.fresh();c[ct]=alg.select(&c[ct],&v,&eff);}},
   K::BitInvert=>c[ct]=alg.xor(&c[ct],&eff),
   K::BitStore0=>c[ct]=alg.select(&c[ct],&vec![],&eff),
   K::BitStore1=>c[ct]=alg.select(&c[ct],&vec![0],&eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},
   _=>return false,
  }
 }
 let o=ops[last];let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);let actual=if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])};stack.is_empty()&&base==vec![0]&&actual==expected
}
