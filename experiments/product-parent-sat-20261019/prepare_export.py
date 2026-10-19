from pathlib import Path
r=Path(__file__).resolve().parent
source=(r.parent/'product-peak-synthesis-20261019/recompute.rs').read_text()
prefix=source[:source.index('fn main(){')]
semantics=source[source.index('  match o.kind {'):source.index('  if i%1000000==0')]
body=r'''
fn main(){
 let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);
 let ops=io::load_ops(&a[1]);let rows:Vec<[u64;9]>=serde_json::from_str(&std::fs::read_to_string(&a[2]).unwrap()).unwrap();
 let no=u64::MAX;let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|&q|q!=no).max().unwrap()as usize+1;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|&q|q!=no).max().unwrap()as usize+1;
 let body_hash=hash(&ops[..ops.len()-96]);assert_eq!(body_hash,"c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04");
 let mut alg=Algebra{next:1,products:HashMap::new(),cap:1024,truncations:0};
 let(mut q,mut c)=initial_inputs(&ops,nq,nb,&mut alg);let mut stack:Vec<E>=vec![];let mut base=vec![0];
 let starts:HashMap<_,_>=rows.iter().enumerate().map(|(j,s)|(s[0]as usize,j)).collect();
 let ends:HashMap<_,_>=rows.iter().enumerate().map(|(j,s)|(s[1]as usize,j)).collect();
 let mut active=HashMap::new();let mut reports:Vec<serde_json::Value>=rows.iter().map(|_|serde_json::json!({})).collect();
 for(i,o)in ops.iter().enumerate(){
  if matches!(o.kind,K::Register|K::AppendToRegister){continue;}
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=stack.pop().unwrap();continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};
  let(t,a,b,ct)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize,o.c_target.0 as usize);
  let product=if o.kind==K::CCX{Some(alg.and(&q[a],&q[b]))}else{None};
  if let Some(&j)=starts.get(&i){
   let s=rows[j];assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[3],s[4],s[5]]);
   let mut qs=HashSet::new();let mut cs=HashSet::new();
   for p in &ops[i..=s[1]as usize]{for w in [p.q_control2.0,p.q_control1.0,p.q_target.0]{if w!=no{qs.insert(w);}}for w in [p.c_condition.0,p.c_target.0]{if w!=no{cs.insert(w);}}}
   let bq:std::collections::BTreeMap<_,_>=qs.iter().map(|&w|(w.to_string(),q[w as usize].clone())).collect();
   let bc:std::collections::BTreeMap<_,_>=cs.iter().map(|&w|(w.to_string(),c[w as usize].clone())).collect();
   let data=serde_json::json!({"status":"EXACT_ABSTRACT_BOUNDARY_OVERAPPROXIMATION","lease":j+1,"first":s[0],"last":s[1],"base_pre_tail_sha3_256":body_hash,"q":bq,"c":bc,"base":base,"stack":stack,"next_atom":alg.next,"expression_cap":alg.cap,"truncations_so_far":alg.truncations});
   let path=format!("{}/boundary-{:02}.json",a[3],j+1);std::fs::write(&path,serde_json::to_vec(&data).unwrap()).unwrap();
   reports[j]=serde_json::json!({"lease":j+1,"start_guard_true":eff==vec![0],"donor_clean":q[s[2]as usize].is_empty(),"donor_untouched":true,"boundary_file":path});
   assert!(active.insert(s[2],j).is_none());
  }
  if !eff.is_empty(){for w in [o.q_control2.0,o.q_control1.0,o.q_target.0]{if let Some(&j)=active.get(&w){reports[j]["donor_untouched"]=serde_json::json!(false);}}}
  if let Some(&j)=ends.get(&i){let s=rows[j];assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[6],s[7],s[8]]);reports[j]["end_guard_true"]=serde_json::json!(eff==vec![0]);assert_eq!(active.remove(&s[2]),Some(j));}
  __SEMANTICS__
  if i%2000000==0{eprintln!("export op {i}, truncated {}",alg.truncations);}
 }
 assert!(stack.is_empty()&&active.is_empty());
 std::fs::write(format!("{}/GLOBAL-PROPERTIES.json",a[3]),serde_json::to_string_pretty(&reports).unwrap()).unwrap();
 println!("exported {} exact boundaries",reports.len());
}
'''.replace('__SEMANTICS__',semantics)
# Avoid reusing the argv name, which is shadowed by the control index below.
body=body.replace('let a:Vec<_>','let argv:Vec<_>').replace('assert_eq!(a.len(),4)','assert_eq!(argv.len(),4)').replace('&a[1]','&argv[1]').replace('&a[2]','&argv[2]').replace('a[3]','argv[3]')
tests=source[source.index('\n#[cfg(test)]mod tests{'):]
(r/'export.rs').write_text(prefix+body+tests)
