
#[cfg(test)]mod public_prefix_policy_tests{use super::*;
 #[test]fn new_route_only_replaces_insufficient_ordinary_fold_and_consumes_flag_once(){
  for enabled in[false,true]{for cap in[1231usize,1232,1233,1234]{for shape in[false,true]{for room in 0..=42{for fmax in 0..=6{for need in 28..=42{let got=public_prefix27_admit(enabled,cap,shape,room,fmax,need);let want=enabled&&cap<1233&&shape&&room>=28&&need>room+fmax;assert_eq!(got,want);if got{assert!(room>=28&&need>room+fmax);}}}}}}}
  PUBLIC_PREFIX27_ROUTE.with(|v|{v.set(true);assert!(v.replace(false));assert!(!v.replace(false));});
 }
}
