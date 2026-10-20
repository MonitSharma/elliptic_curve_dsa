// Nomination only. Full arbitrary-cut algebra remains the acceptance test.
struct ScopeFrame{q:HashMap<usize,H>,c:HashMap<usize,H>,base:H,stack:Vec<H>,unknown:bool}
fn scoped_value(map:&mut HashMap<usize,H>,id:usize,f:&mut Fingerprints,unknown:bool)->H{
 if let Some(&v)=map.get(&id){v}else if unknown{let v=f.fresh();map.insert(id,v);v}else{0}
}
fn scoped_product_keys(ops:&[Op])->HashMap<usize,H>{
 let no=u64::MAX;let mut f=Fingerprints{next:900000000,products:HashMap::new()};
 let mut root=ScopeFrame{q:HashMap::new(),c:HashMap::new(),base:1,stack:vec![],unknown:false};
 for o in ops{if o.kind==K::AppendToRegister{if o.q_target.0!=no{root.q.entry(o.q_target.0 as usize).or_insert_with(||f.fresh());}if o.c_target.0!=no{root.c.entry(o.c_target.0 as usize).or_insert_with(||f.fresh());}}}
 let mut frames=vec![root];let mut keys=HashMap::new();
 for(i,o)in ops.iter().enumerate(){
  if o.kind==K::PushCondition{
   for fr in &mut frames{let v=scoped_value(&mut fr.c,o.c_condition.0 as usize,&mut f,fr.unknown);fr.stack.push(fr.base);fr.base=f.and(fr.base,v);}
   frames.push(ScopeFrame{q:HashMap::new(),c:HashMap::new(),base:1,stack:vec![],unknown:true});continue;
  }
  if o.kind==K::PopCondition{assert!(frames.len()>1);frames.pop();for fr in &mut frames{fr.base=fr.stack.pop().unwrap();}continue;}
  let deepest=frames.len()-1;
  for(depth,fr)in frames.iter_mut().enumerate(){
   let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
   let cond=if o.c_condition.0==no{1}else{scoped_value(&mut fr.c,o.c_condition.0 as usize,&mut f,fr.unknown)};let eff=f.and(fr.base,cond);
   if eff==0{continue;}
   match o.kind{
    K::X=>{let v=scoped_value(&mut fr.q,t,&mut f,fr.unknown);fr.q.insert(t,v^eff);},
    K::CX=>{let av=scoped_value(&mut fr.q,a,&mut f,fr.unknown);let tv=scoped_value(&mut fr.q,t,&mut f,fr.unknown);fr.q.insert(t,tv^f.and(av,eff));},
    K::CCX=>{let av=scoped_value(&mut fr.q,a,&mut f,fr.unknown);let bv=scoped_value(&mut fr.q,b,&mut f,fr.unknown);let tv=scoped_value(&mut fr.q,t,&mut f,fr.unknown);let product=f.and(av,bv);let ev=f.and(product,eff);if depth==deepest{keys.insert(i,ev);}fr.q.insert(t,tv^ev);},
    K::Swap=>{let av=scoped_value(&mut fr.q,a,&mut f,fr.unknown);let tv=scoped_value(&mut fr.q,t,&mut f,fr.unknown);let v=f.and(av^tv,eff);fr.q.insert(a,av^v);fr.q.insert(t,tv^v);},
    K::R|K::Hmr=>{let tv=scoped_value(&mut fr.q,t,&mut f,fr.unknown);fr.q.insert(t,f.select(tv,0,eff));if o.kind==K::Hmr{let cv=scoped_value(&mut fr.c,ct,&mut f,fr.unknown);let v=f.fresh();fr.c.insert(ct,f.select(cv,v,eff));}},
    K::BitInvert=>{let v=scoped_value(&mut fr.c,ct,&mut f,fr.unknown);fr.c.insert(ct,v^eff);},
    K::BitStore0|K::BitStore1=>{let v=scoped_value(&mut fr.c,ct,&mut f,fr.unknown);fr.c.insert(ct,f.select(v,u128::from(o.kind==K::BitStore1),eff));},
    K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},_=>panic!("unhandled scoped operation")
   }
  }
 }
 assert_eq!(frames.len(),1);keys
}
#[cfg(test)]mod scoped_nomination_tests{
 use super::*;
 #[test]fn cofactored_scope_nominates_symmetric_triple_even_when_global_guard_obscures_it(){let n=u64::MAX;let ops=vec![make(K::PushCondition,n,n,n,n,0),make(K::CCX,0,1,2,n,n),make(K::CX,n,0,1,n,n),make(K::X,n,n,1,n,n),make(K::CCX,0,1,3,n,n),make(K::PopCondition,n,n,n,n,n)];let k=scoped_product_keys(&ops);assert_eq!(k[&1],k[&4]);assert!(local_proof(&ops,1,4,4,1));let mut bad=ops.clone();bad.remove(3);let k=scoped_product_keys(&bad);assert_ne!(k[&1],k[&3]);assert!(!local_proof(&bad,1,3,4,1));}
 #[test]fn nested_scope_updates_parent_snapshot_and_guard_mutation(){let n=u64::MAX;let mut ops=vec![make(K::PushCondition,n,n,n,n,0),make(K::CCX,0,1,2,n,n),make(K::PushCondition,n,n,n,n,1),make(K::X,n,n,0,n,n),make(K::PopCondition,n,n,n,n,n),make(K::CCX,0,1,3,n,n),make(K::PopCondition,n,n,n,n,n)];let k=scoped_product_keys(&ops);assert_ne!(k[&1],k[&5]);assert!(!local_proof(&ops,1,5,4,2));ops[3]=make(K::BitInvert,n,n,n,0,n);let k=scoped_product_keys(&ops);assert_eq!(k[&1],k[&5]);assert!(local_proof(&ops,1,5,4,2));}
}
