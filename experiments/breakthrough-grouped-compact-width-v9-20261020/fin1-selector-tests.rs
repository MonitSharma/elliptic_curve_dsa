
#[cfg(test)]mod compact_fin1_selector_tests{
 use super::*;
 #[test]fn exact_equal_cap_fin1_route_preserves_all_shape_constraints(){
  for cap in [1233usize,1234,1235]{for enabled in [false,true]{std::env::set_var("PEBBLE_HARD_CAP",cap.to_string());std::env::set_var("EXACT_CMP_COMPACT",if enabled{"1"}else{"0"});for fin in [0,1,2]{for mw in [55,56,57]{for no_esh in [false,true]{for ttm in [false,true]{let got=super::super::super::super::pingpong::with_phase_cap(Some(cap),||selected(mw,fin,ttm,no_esh));let want=mw==56&&fin==1&&!ttm&&no_esh&&(cap<1234||(enabled&&cap==1234));assert_eq!(got,want);}}}}}}
  std::env::remove_var("EXACT_CMP_COMPACT");std::env::set_var("PEBBLE_HARD_CAP","1234");
 }
}
