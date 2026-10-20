
#[cfg(test)]mod wide_loan_policy_tests{
 use super::*;
 #[test]fn narrow_consumer_loan_scope_tracks_both_preflight_and_runtime(){
  for hard in [1232,1233,1234,1248,1256,1264,1280,1296,1360]{std::env::set_var("PEBBLE_HARD_CAP",hard.to_string());for t in 0..150{for rev in [false,true]{assert_eq!(reverse_loan_selected(rev,t),rev&&(124..=126).contains(&t)&&hard<=1248);assert_eq!(carry_loan_selected(rev,t),!rev&&(128..137).contains(&t)&&hard<=1248);}}}
  std::env::set_var("PEBBLE_HARD_CAP","1234");
 }
}
