
#[cfg(test)]mod exact_early_drop_policy_tests{
 use super::*;
 #[test]fn new_early_range_retains_original_policy_and_only_selects_existing_exact_plan(){
  std::env::remove_var("STACK_DROP130_RESEARCH");std::env::remove_var("STACK_DROP_EARLY_RESEARCH");let baseline:Vec<_>=(0..145).flat_map(|t|[y28_drop(t,false),y28_drop(t,true)]).collect();
  for on in [false,true]{for early in [false,true]{std::env::set_var("STACK_DROP130_RESEARCH",if on{"1"}else{"0"});std::env::set_var("STACK_DROP_EARLY_RESEARCH",if early{"1"}else{"0"});for t in 0..145{for rev in [false,true]{let chosen=on&&((!rev&&((if early{127}else{130})..137).contains(&t))||(rev&&((if early{122}else{124})..127).contains(&t)));assert_eq!(y28_drop(t,rev),if chosen{3}else{baseline[2*t+usize::from(rev)]});}}}}
  std::env::remove_var("STACK_DROP130_RESEARCH");std::env::remove_var("STACK_DROP_EARLY_RESEARCH");
 }
}
