// Backward dependence pruning for value equality only. Phase repair is proved
// separately by the unchanged lease rewrite. No samples or hashes accept proofs.
fn dependency_cone(ops:&[Op],first:usize,last:usize)->Vec<Op>{
 let no=u64::MAX;let slice=&ops[first..=last];let n=slice.len();let mut parent=vec![None;n];let mut closes=HashMap::new();let mut stack=vec![];
 for(i,o)in slice.iter().enumerate(){parent[i]=stack.last().copied();if o.kind==K::PushCondition{stack.push(i);}else if o.kind==K::PopCondition{let p=stack.pop().expect("balanced cut scope");closes.insert(p,i);}}
 assert!(stack.is_empty());let mut q=HashSet::from([slice[n-1].q_control1.0,slice[n-1].q_control2.0]);let mut c=HashSet::new();if slice[n-1].c_condition.0!=no{c.insert(slice[n-1].c_condition.0);}let mut selected=vec![false;n];selected[0]=true;selected[n-1]=true;
 for i in(0..n-1).rev(){let o=slice[i];let writes_q=matches!(o.kind,K::X|K::CX|K::CCX|K::Swap|K::R|K::Hmr)&&(q.contains(&o.q_target.0)||o.kind==K::Swap&&q.contains(&o.q_control1.0));let writes_c=matches!(o.kind,K::BitInvert|K::BitStore0|K::BitStore1|K::Hmr)&&c.contains(&o.c_target.0);
  if !writes_q&&!writes_c&&i!=0{continue;}selected[i]=true;
  if writes_q{for w in[o.q_control1.0,o.q_control2.0,o.q_target.0]{if w!=no{q.insert(w);}}}
  if o.c_condition.0!=no{c.insert(o.c_condition.0);}let mut up=parent[i];while let Some(p)=up{selected[p]=true;selected[closes[&p]]=true;c.insert(slice[p].c_condition.0);up=parent[p];}
 }
 slice.iter().zip(selected).filter_map(|(o,yes)|yes.then_some(*o)).collect()
}
fn cone_local_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool{
 if last-first>200000{return false;}let reduced=dependency_cone(ops,first,last);local_proof(&reduced,0,reduced.len()-1,nq,nb)
}
#[cfg(test)]mod cone_tests{
 use super::*;
 #[test]fn pruned_proof_keeps_all_nested_guard_and_value_dependencies_and_rejects_faults(){let no=u64::MAX;for conditional in[false,true]{let mut ops=vec![make(K::CCX,0,1,2,no,if conditional{0}else{no})];for _ in 0..32{ops.push(make(K::X,no,no,7,no,no));}ops.push(make(K::PushCondition,no,no,no,no,1));ops.push(make(K::CX,no,0,1,no,no));ops.push(make(K::X,no,no,1,no,no));ops.push(make(K::PopCondition,no,no,no,no,no));ops.push(make(K::CCX,0,1,3,no,if conditional{0}else{no}));let end=ops.len()-1;let reduced=dependency_cone(&ops,0,end);assert!(reduced.len()<ops.len());assert!(local_proof(&ops,0,end,8,2));assert!(cone_local_proof(&ops,0,end,8,2));ops.remove(35);let end=ops.len()-1;assert!(!local_proof(&ops,0,end,8,2));assert!(!cone_local_proof(&ops,0,end,8,2));}}
 #[test]fn guard_snapshot_reads_before_overwrite_are_retained(){let no=u64::MAX;let ops=vec![make(K::CCX,0,1,2,no,0),make(K::PushCondition,no,no,no,no,1),make(K::BitInvert,no,no,no,0,no),make(K::X,no,no,1,no,0),make(K::PopCondition,no,no,no,no,no),make(K::CCX,0,1,3,no,0)];let reduced=dependency_cone(&ops,0,5);assert!(reduced.iter().any(|o|o.kind==K::BitInvert));assert_eq!(local_proof(&ops,0,5,4,2),cone_local_proof(&ops,0,5,4,2));assert!(!cone_local_proof(&ops,0,5,4,2));}
}
