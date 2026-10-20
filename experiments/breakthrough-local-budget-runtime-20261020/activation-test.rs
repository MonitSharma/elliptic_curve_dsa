
#[cfg(test)]mod physical_cap_activation_tests{
 use super::*;
 #[test]fn automatic_loans_honor_physical_cap_with_original_global_budget(){
  let mut c=Builder::new();let _padding=c.alloc_qubits(1228);core_loans::force(None);core_loans_fin1::force(None);
  for hard in [1234,1233,1232]{std::env::set_var("PEBBLE_HARD_CAP",hard.to_string());super::super::super::pingpong::with_phase_cap(Some(1234),||{assert_eq!(physical_fold_cap(),hard);assert_eq!(core_loans::selected(&c,56,0,false,true,true),hard<1234);assert_eq!(core_loans_fin1::selected(56,1,false,true),hard<1234);assert!(!core_loans::selected(&c,57,0,false,true,true));assert!(!core_loans_fin1::selected(56,2,false,true));});}
  std::env::set_var("PEBBLE_HARD_CAP","1234");
 }
}
