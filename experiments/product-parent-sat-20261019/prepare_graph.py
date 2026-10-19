"""Retain exact definitions behind opaque atoms, exporting a bounded cone."""
from pathlib import Path
r=Path(__file__).resolve().parent
source=(r/'export.rs').read_text()
prefix=source[:source.index('fn main(){')]
old='struct Algebra { next:u32, products:HashMap<Triple,u32>, cap:usize, truncations:u64 }'
assert prefix.count(old)==1
prefix=prefix.replace(old,'struct Algebra { next:u32, products:HashMap<Triple,u32>, cap:usize, truncations:u64, definitions:HashMap<u32,(u8,E,E)> }')
old='fn limit(&mut self,e:E)->E {if e.len()>self.cap {self.truncations+=1;self.fresh()} else {e}}'
new='fn limit(&mut self,e:E)->E {if e.len()>self.cap {self.truncations+=1;let v=self.fresh();self.definitions.insert(v[0],(0,e,vec![]));v} else {e}}'
assert prefix.count(old)==1;prefix=prefix.replace(old,new)
old='let v=self.next;self.next+=1;self.products.insert(t,v);vec![v]'
new='let v=self.next;self.next+=1;self.products.insert(t,v);self.definitions.insert(v,(1,a.clone(),b.clone()));vec![v]'
assert prefix.count(old)==1;prefix=prefix.replace(old,new)
semantics=source[source.index('  match o.kind {'):source.index('  if i%2000000==0')]
body=r'''
fn main(){
 let argv:Vec<_>=std::env::args().collect();assert_eq!(argv.len(),5);
 let ops=io::load_ops(&argv[1]);let roots:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&argv[2]).unwrap()).unwrap();
 let boundary:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&argv[3]).unwrap()).unwrap();
 let first=boundary["first"].as_u64().unwrap()as usize;
 let body_hash=hash(&ops[..ops.len()-96]);assert_eq!(body_hash,"c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04");
 let no=u64::MAX;let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|&q|q!=no).max().unwrap()as usize+1;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|&q|q!=no).max().unwrap()as usize+1;
 let mut alg=Algebra{next:1,products:HashMap::new(),cap:1024,truncations:0};
 let(mut q,mut c)=initial_inputs(&ops,nq,nb,&mut alg);let mut stack:Vec<E>=vec![];let mut base=vec![0];
 for(i,o)in ops.iter().enumerate(){
  if i==first{
   assert_eq!(base,serde_json::from_value::<E>(boundary["base"].clone()).unwrap());
   assert_eq!(stack,serde_json::from_value::<Vec<E>>(boundary["stack"].clone()).unwrap());
   for(k,e)in boundary["q"].as_object().unwrap(){assert_eq!(q[k.parse::<usize>().unwrap()],serde_json::from_value::<E>(e.clone()).unwrap());}
   for(k,e)in boundary["c"].as_object().unwrap(){assert_eq!(c[k.parse::<usize>().unwrap()],serde_json::from_value::<E>(e.clone()).unwrap());}
   let root_atoms:Vec<u32>=serde_json::from_value(roots["boundary_atoms"].clone()).unwrap();
   let mut todo:std::collections::VecDeque<_>=root_atoms.iter().map(|&a|(a,0usize)).collect();let mut seen=HashSet::new();let mut definitions=std::collections::BTreeMap::new();let mut references=0;let mut frontier=0;
   while let Some((atom,depth))=todo.pop_front(){if atom==0||!seen.insert(atom){continue;}if let Some(d)=alg.definitions.get(&atom){
    if depth>=16||references+d.1.len()+d.2.len()>2_000_000{frontier+=1;continue;}
    references+=d.1.len()+d.2.len();definitions.insert(atom.to_string(),d.clone());
    for &v in d.1.iter().chain(&d.2){if v!=0{todo.push_back((v,depth+1));}}
   }}
   let data=serde_json::json!({"status":"EXACT_GLOBAL_ATOM_RELATION_CONE","base_pre_tail_sha3_256":body_hash,"boundary_sha256":roots["boundary_sha256"],"first":first,"definitions":definitions,"root_atoms":root_atoms,"reference_count":references,"unexpanded_definition_frontier":frontier,"max_depth":16,"reference_budget":2_000_000,"global_definition_count":alg.definitions.len(),"interpretation":"Every included atom relation is exact. Every omitted relation leaves an independent abstract variable; this can only weaken the proof."});
   std::fs::write(&argv[4],serde_json::to_vec(&data).unwrap()).unwrap();println!("exported {} exact definitions; references={references}; frontier={frontier}",definitions.len());break;
  }
  if matches!(o.kind,K::Register|K::AppendToRegister){continue;}
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=stack.pop().unwrap();continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};
  let(t,a,b,ct)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize,o.c_target.0 as usize);
  let product=if o.kind==K::CCX{Some(alg.and(&q[a],&q[b]))}else{None};
  __SEMANTICS__
  if i%2000000==0{eprintln!("relation op {i}, definitions {}",alg.definitions.len());}
 }
}
'''.replace('__SEMANTICS__',semantics)
tests=source[source.index('\n#[cfg(test)]mod tests{'):]
s=(prefix+body+tests).replace('Algebra{next:','Algebra{definitions:HashMap::new(),next:')
s+=r'''
#[cfg(test)]mod relation_tests{
 use super::*;
 fn atom(a:u32,inputs:&[bool],alg:&Algebra)->bool{if a==0{return true;}if a as usize<=inputs.len(){return inputs[a as usize-1];}let d=&alg.definitions[&a];let left=value(&d.1,inputs,alg);if d.0==0{left}else{left&&value(&d.2,inputs,alg)}}
 fn value(e:&E,inputs:&[bool],alg:&Algebra)->bool{e.iter().fold(false,|a,&b|a^atom(b,inputs,alg))}
 #[test]fn and_and_truncated_xor_definitions_match_all_basis_inputs(){let mut a=Algebra{definitions:HashMap::new(),next:3,products:HashMap::new(),cap:1,truncations:0};let p=a.and(&vec![1],&vec![2]);let x=a.xor(&vec![1],&vec![2]);for b in 0..4{let ins=[b&1!=0,b&2!=0];assert_eq!(value(&p,&ins,&a),ins[0]&&ins[1]);assert_eq!(value(&x,&ins,&a),ins[0]^ins[1]);}}
 #[test]fn conditional_update_graph_matches_all_basis_inputs(){let mut a=Algebra{definitions:HashMap::new(),next:4,products:HashMap::new(),cap:1,truncations:0};let e=a.select(&vec![1],&vec![2],&vec![3]);for b in 0..8{let ins=[b&1!=0,b&2!=0,b&4!=0];assert_eq!(value(&e,&ins,&a),if ins[2]{ins[1]}else{ins[0]});}}
 #[test]fn incorrect_truncation_definition_is_detected(){let mut a=Algebra{definitions:HashMap::new(),next:3,products:HashMap::new(),cap:1,truncations:0};let e=a.xor(&vec![1],&vec![2]);a.definitions.insert(e[0],(0,vec![0,1,2],vec![]));assert!((0..4).any(|b|{let ins=[b&1!=0,b&2!=0];value(&e,&ins,&a)!=(ins[0]^ins[1])}));}
}
'''
(r/'graph.rs').write_text(s)
