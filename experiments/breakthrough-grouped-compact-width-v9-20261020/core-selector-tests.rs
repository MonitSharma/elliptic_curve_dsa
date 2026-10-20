
#[cfg(test)]mod compact_core_selector_tests{
 use super::*;
 #[test]fn checked_equal_cap_route_matches_estimate_and_preserves_original_admission(){
  for cap in [1233usize,1234,1235]{for enabled in [false,true]{std::env::set_var("PEBBLE_HARD_CAP",cap.to_string());std::env::set_var("EXACT_CMP_COMPACT",if enabled{"1"}else{"0"});for room in 0..=12{let mut c=Builder::new();let q=c.alloc_qubits(cap-room);assert_eq!(c.active_qubits()as usize,cap-room);for fin in [0,1]{for mw in [55,56,57]{for no_esh in [false,true]{for ttm in [false,true]{for loan in [false,true]{let got=super::super::super::super::pingpong::with_phase_cap(Some(cap),||selected(&c,mw,fin,ttm,loan,no_esh));let want=fin==0&&no_esh&&mw==56&&(cap<1234||(enabled&&cap==1234))&&room+usize::from(ttm)<=10;assert_eq!(got,want,"cap{cap} enabled{enabled} room{room} fin{fin} mw{mw} no_esh{no_esh} ttm{ttm} loan{loan}");}}}}}drop(q);}}}
  std::env::remove_var("EXACT_CMP_COMPACT");std::env::set_var("PEBBLE_HARD_CAP","1234");
 }
}
