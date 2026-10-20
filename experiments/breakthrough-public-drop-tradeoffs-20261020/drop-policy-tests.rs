
fn public_reverse_drop_profile(profile:&str,t:usize)->Option<usize>{if !(124..127).contains(&t){return None;}let values=match profile{"rmin"=>[1,2,3],"r1"=>[0,1,3],"r2"=>[0,2,3],"r9"=>[1,2,2],_=>return None};Some(values[t-124])}
#[cfg(test)]mod public_reverse_drop_policy_tests{use super::*;
 #[test]fn only_declared_reverse_profiles_change_and_keep_original_forward_policy(){
  std::env::remove_var("STACK_DROP130_RESEARCH");std::env::remove_var("STACK_REVERSE_DROP_PROFILE");let base:Vec<_>=(0..145).flat_map(|t|[y28_drop(t,false),y28_drop(t,true)]).collect();
  for on in[false,true]{for(profile,values)in[("t21",None),("rmin",Some([1,2,3])),("r1",Some([0,1,3])),("r2",Some([0,2,3])),("r9",Some([1,2,2]))]{std::env::set_var("STACK_DROP130_RESEARCH",if on{"1"}else{"0"});std::env::set_var("STACK_REVERSE_DROP_PROFILE",profile);for t in 0..145{for rev in[false,true]{let expected=if on&&rev&&(124..127).contains(&t)&&values.is_some(){values.unwrap()[t-124]}else if on&&((!rev&&(130..137).contains(&t))||(rev&&(124..127).contains(&t))){3}else{base[2*t+usize::from(rev)]};assert_eq!(y28_drop(t,rev),expected);}}}}
  std::env::remove_var("STACK_DROP130_RESEARCH");std::env::remove_var("STACK_REVERSE_DROP_PROFILE");
 }
}
