// This module is appended to an exact immutable prefix kernel. The query is
// pure: it never allocates prefix atoms or changes product-cache history.
fn row_xor(a:&Affine,b:&Affine)->Option<Affine>{
 let mut result=Vec::with_capacity(a.atoms.len()+b.atoms.len());let(mut i,mut j)=(0,0);
 while i<a.atoms.len()||j<b.atoms.len(){if j==b.atoms.len()||(i<a.atoms.len()&&a.atoms[i]<b.atoms[j]){result.push(a.atoms[i]);i+=1;}else if i==a.atoms.len()||b.atoms[j]<a.atoms[i]{result.push(b.atoms[j]);j+=1;}else{i+=1;j+=1;}}
 (result.len()<=4096).then_some(Affine{constant:a.constant^b.constant,atoms:result})
}
fn reduce(mut row:Affine,basis:&std::collections::BTreeMap<u64,Affine>)->Option<Affine>{
 while let Some(&pivot)=row.atoms.first(){if let Some(other)=basis.get(&pivot){row=row_xor(&row,other)?;}else{break;}}Some(row)
}
fn cofactor(facts:&[Affine],queries:&[Affine])->Option<(bool,Vec<Option<bool>>)> {
 if facts.len()>32{return None;}let mut basis=std::collections::BTreeMap::new();
 for fact in facts{let mut row=fact.clone();row.constant^=true;row=reduce(row,&basis)?;
  if row.atoms.is_empty(){if row.constant{return Some((true,vec![None;queries.len()]));}}else{basis.insert(row.atoms[0],row);}
 }
 let answers=queries.iter().map(|q|reduce(q.clone(),&basis).map(|r|if r.atoms.is_empty(){Some(r.constant)}else{None})).collect::<Option<Vec<_>>>()?;Some((false,answers))
}
pub(crate) fn run_cofactor_census(ops:&[Op])->serde_json::Value {
 let mut state=Support::new(ops);let mut facts:Vec<Affine>=Vec::new();let mut lengths=Vec::new();let mut ccx=0;let mut global_keep=0;let mut tested=0;let mut caps=0;let mut unreachable=0;let mut proposals=Vec::new();let started=std::time::Instant::now();
 for(at,op) in ops.iter().enumerate(){
  if op.kind==OperationType::PushCondition{lengths.push(facts.len());facts.push(state.bits[op.c_condition.0 as usize].clone());let _=state.step(op);continue;}
  if op.kind==OperationType::PopCondition{facts.truncate(lengths.pop().unwrap());let _=state.step(op);continue;}
  if op.kind!=OperationType::CCX{let _=state.step(op);continue;}ccx+=1;
  let a=state.qubits[op.q_control1.0 as usize].clone();let b=state.qubits[op.q_control2.0 as usize].clone();let mut actual=facts.clone();if op.c_condition!=NO_BIT{actual.push(state.bits[op.c_condition.0 as usize].clone());}
  let result=if actual.is_empty(){None}else{tested+=1;cofactor(&actual,&[a.clone(),b.clone()])};
  let old=state.step(op);if !matches!(old,Rewrite::Keep){continue;}global_keep+=1;
  match result{None=>{if !actual.is_empty(){caps+=1;}},Some((true,_))=>{unreachable+=1;},Some((false,values))=>{
   let novel_a=!a.atoms.is_empty()&&values[0].is_some();let novel_b=!b.atoms.is_empty()&&values[1].is_some();if !novel_a&&!novel_b{continue;}
   assert!(proposals.len()<10000,"predeclared proposal artifact cap reached");
   let as_json=|v:&Affine|serde_json::json!({"constant":v.constant,"atoms":v.atoms});
   proposals.push(serde_json::json!({"op":at,"target":op.q_target.0,"controls":[op.q_control1.0,op.q_control2.0],"cofactored_controls":values,"guard_facts":actual.iter().map(as_json).collect::<Vec<_>>(),"control_forms":[as_json(&a),as_json(&b)],"additional_Q_MR_B":[0,0,0],"T_saved_when_guard_executes":1}));
  }}
 }
 assert!(lengths.is_empty()&&facts.is_empty());serde_json::json!({"status":"TERMINAL_SOURCE_ONLY_AFFINE_COFACTOR","CCX":ccx,"global_Keep":global_keep,"guarded_queries":tested,"bounded_query_caps":caps,"additional_unreachable_guards":unreachable,"novel_control_constant_sites":proposals.len(),"proposals":proposals,"elapsed_seconds":started.elapsed().as_secs_f64(),"sampled_inputs":0,"rewrites":0})
}
#[cfg(test)]mod cofactor_tests{
 use super::*;fn f(c:bool,a:&[u64])->Affine{Affine{constant:c,atoms:a.to_vec()}}
 #[test]fn exact_guard_relations(){assert_eq!(cofactor(&[f(false,&[1])],&[f(false,&[1]),f(true,&[1])]),Some((false,vec![Some(true),Some(false)])));assert_eq!(cofactor(&[f(false,&[1,2]),f(true,&[2])],&[f(false,&[1])]),Some((false,vec![Some(true)])));assert_eq!(cofactor(&[f(false,&[1]),f(true,&[1])],&[f(false,&[2])]),Some((true,vec![None])));}
 #[test]fn unrelated_opaque_atoms_stay_unknown(){assert_eq!(cofactor(&[f(false,&[1])],&[f(false,&[2]),f(false,&[1,2])]),Some((false,vec![None,None])));let guard=f(false,&[1]);let snapshot=guard.clone();let mut current=guard;current.constant^=true;assert_eq!(cofactor(&[snapshot],&[current]),Some((false,vec![Some(false)])));}
}
