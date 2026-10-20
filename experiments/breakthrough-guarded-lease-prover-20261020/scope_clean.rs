// Conservative exact zero analysis; no fingerprints establish cleanliness.
struct CleanFrame{q:Vec<bool>,c:HashMap<usize,i8>,default:i8,base:i8,stack:Vec<i8>}
fn scope_clean_donors(ops:&[Op],nq:usize,keys:&HashMap<usize,H>)->HashMap<usize,Vec<usize>>{
 let no=u64::MAX;let mut root=CleanFrame{q:vec![true;nq],c:HashMap::new(),default:0,base:1,stack:vec![]};
 for o in ops{if o.kind==K::AppendToRegister{if o.q_target.0!=no{root.q[o.q_target.0 as usize]=false;}if o.c_target.0!=no{root.c.insert(o.c_target.0 as usize,-1);}}}
 let mut frames=vec![root];let mut scopes=vec![];let mut prior=HashMap::new();let mut touches=vec![None;nq];let mut result=HashMap::new();
 for(i,o)in ops.iter().enumerate(){
  if o.kind==K::PushCondition{let clean=frames.last().unwrap().q.clone();for fr in &mut frames{let cv=*fr.c.get(&(o.c_condition.0 as usize)).unwrap_or(&fr.default);fr.stack.push(fr.base);fr.base=tri_and(fr.base,cv);}let mut c=HashMap::new();c.insert(o.c_condition.0 as usize,1);frames.push(CleanFrame{q:clean,c,default:-1,base:1,stack:vec![]});scopes.push(i);continue;}
  if o.kind==K::PopCondition{frames.pop();for fr in &mut frames{fr.base=fr.stack.pop().unwrap();}scopes.pop();continue;}
  if o.kind==K::CCX{if let Some(&key)=keys.get(&i){if let Some(first)=prior.insert((scopes.clone(),key),i){let fr=frames.last().unwrap();let donors=(0..nq).filter(|&d|fr.q[d]&&touches[d].is_none_or(|j|j<first)&&![o.q_control1.0,o.q_control2.0,o.q_target.0].contains(&(d as u64))).take(64).collect::<Vec<_>>();if !donors.is_empty(){result.insert(i,donors);}}}}
  for fr in &mut frames{
   let cc=if o.c_condition.0==no{1}else{*fr.c.get(&(o.c_condition.0 as usize)).unwrap_or(&fr.default)};let ce=tri_and(fr.base,cc);if ce==0{continue;}
   let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
   match o.kind{
    K::R|K::Hmr=>{if ce==1{fr.q[t]=true;}if o.kind==K::Hmr{fr.c.insert(ct,-1);}},
    K::X=>fr.q[t]=false,
    K::CX=>{if !fr.q[a]{fr.q[t]=false;}},
    K::CCX=>{if !fr.q[a]&&!fr.q[b]{fr.q[t]=false;}},
    K::Swap=>{let ta=fr.q[t];let aa=fr.q[a];if ce==1{fr.q[t]=aa;fr.q[a]=ta;}else{fr.q[t]=ta&&aa;fr.q[a]=ta&&aa;}},
    K::BitStore0|K::BitStore1=>{let v=i8::from(o.kind==K::BitStore1);let old=*fr.c.get(&ct).unwrap_or(&fr.default);fr.c.insert(ct,if ce==1||old==v{v}else{-1});},
    K::BitInvert=>{let old=*fr.c.get(&ct).unwrap_or(&fr.default);fr.c.insert(ct,if ce==1&&old>=0{1-old}else{-1});},
    K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},_=>panic!("unknown clean operation")
   }
  }
  if o.kind!=K::AppendToRegister{for w in [o.q_control1.0,o.q_control2.0,o.q_target.0]{if w!=no{touches[w as usize]=Some(i);}}}
 }
 assert_eq!(frames.len(),1);result
}
#[cfg(test)]mod scope_clean_tests{
 use super::*;use quantum_ecc::circuit::RegisterId;
 fn annotation(q:u64)->Op{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);o}
 #[test]fn conditional_reset_proves_donor_only_inside_scope(){let n=u64::MAX;let ops=vec![annotation(4),make(K::PushCondition,n,n,n,n,0),make(K::R,n,n,4,n,n),make(K::CCX,0,1,2,n,n),make(K::CCX,0,1,3,n,n),make(K::PopCondition,n,n,n,n,n)];let keys=scoped_product_keys(&ops);let donors=scope_clean_donors(&ops,5,&keys);assert!(donors[&4].contains(&4));let mut broken=ops.clone();broken[2]=make(K::Z,n,n,4,n,n);let d=scope_clean_donors(&broken,5,&scoped_product_keys(&broken));assert!(!d.get(&4).is_some_and(|v|v.contains(&4)));}
 #[test]fn intervening_read_and_nested_unknown_reset_cannot_justify_donor(){let n=u64::MAX;let ops=vec![annotation(4),make(K::PushCondition,n,n,n,n,0),make(K::PushCondition,n,n,n,n,1),make(K::R,n,n,4,n,n),make(K::PopCondition,n,n,n,n,n),make(K::CCX,0,1,2,n,n),make(K::CCX,0,1,3,n,n),make(K::PopCondition,n,n,n,n,n)];let d=scope_clean_donors(&ops,5,&scoped_product_keys(&ops));assert!(!d.get(&6).is_some_and(|v|v.contains(&4)));let mut good=ops.clone();good[2]=make(K::PushCondition,n,n,n,n,0);let d=scope_clean_donors(&good,5,&scoped_product_keys(&good));assert!(d[&6].contains(&4));good.insert(6,make(K::Z,n,n,4,n,n));let d=scope_clean_donors(&good,5,&scoped_product_keys(&good));assert!(!d.get(&7).is_some_and(|v|v.contains(&4)));}
}
