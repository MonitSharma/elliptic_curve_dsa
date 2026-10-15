// Proposal heuristic only. No transformation or certificate relies on tags.
fn first_use_tags(ops:&[Op],nb:usize)->Vec<Option<(u64,u64)>> {
    let mut epochs=vec![0u64;nb];let mut tags=vec![None;ops.len()];
    for (i,o) in ops.iter().enumerate(){
        if o.kind==K::CCX && i>=3 && i+2<ops.len(){
            let (a,b,c,d,e)=(ops[i-3],ops[i-2],ops[i-1],ops[i+1],ops[i+2]);
            let temp=a.c_target;let valid=b.c_condition;
            if a.kind==K::BitStore1 && a.c_condition==NO_BIT &&
               b.kind==K::BitInvert && b.c_target==temp && valid!=NO_BIT && valid.0>=45701 &&
               temp!=valid && c.kind==K::PushCondition && c.c_condition==temp &&
               o.c_condition==NO_BIT && d.kind==K::BitStore1 && d.c_target==valid &&
               d.c_condition==NO_BIT && e.kind==K::PopCondition {
                tags[i]=Some((valid.0,epochs[valid.0 as usize]));
            }
        }
        // Between tagged computes the flag may only stay unchanged or set1.
        // Any possible clearing/toggling/random overwrite ends the epoch,
        // including conditional writes whose condition might be inactive.
        if matches!(o.kind,K::BitStore0|K::BitInvert|K::Hmr) && o.c_target!=NO_BIT {
            epochs[o.c_target.0 as usize]=epochs[o.c_target.0 as usize].checked_add(1).unwrap();
        }
    }
    tags
}
fn same_first_use_epoch(uses:&[usize],tags:&[Option<(u64,u64)>])->bool {
    let Some(tag)=tags[uses[0]] else{return false;};
    uses.iter().all(|i|tags[*i]==Some(tag))
}
#[cfg(test)]mod global_tag_tests{use super::*;
 fn pattern(valid:u64,temp:u64)->Vec<Op>{vec![store(temp,true),gate(K::BitInvert,None,None,None,Some(temp),Some(valid)),push(temp),gate(K::CCX,Some(0),Some(1),Some(2),None,None),store(valid,true),pop()]}
 #[test]fn monotone_compute_groups_are_rejected_but_cleared_epochs_are_distinct(){
  let mut p=pattern(45701,45702);p.extend(pattern(45701,45702));
  let tags=first_use_tags(&p,45703);assert!(same_first_use_epoch(&[3,9],&tags));
  p.insert(6,store(45701,false));let tags=first_use_tags(&p,45703);assert!(!same_first_use_epoch(&[3,10],&tags));
 }
 #[test]fn unknown_overwrites_and_nonexact_shapes_never_share_a_tag(){
  for writer in [gate(K::BitInvert,None,None,None,Some(45701),Some(0)),gate(K::Hmr,None,None,Some(0),Some(45701),None)]{
   let mut p=pattern(45701,45702);p.push(writer);p.extend(pattern(45701,45702));
   assert!(!same_first_use_epoch(&[3,10],&first_use_tags(&p,45703)));
  }
  let mut p=pattern(45701,45702);p[3].c_condition=BitId(0);
  assert!(first_use_tags(&p,45703)[3].is_none());
  assert!(first_use_tags(&pattern(100,101),102)[3].is_none());
 }
}
