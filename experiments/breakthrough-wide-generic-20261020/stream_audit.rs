use crate::circuit::Op;
#[test]#[ignore]fn frozen_wide_stream_with_original_generic_recipe(){
 let input=std::env::var("WIDE_AUDIT_INPUT").unwrap();let output=std::env::var("WIDE_AUDIT_OUTPUT").unwrap();let hard=std::env::var("WIDE_AUDIT_CAP").unwrap();
 super::clear_process_env();super::install_skywalk_submission_recipe();std::env::set_var("EXACT_PAIR_CARRY","1");if super::LEAPFROG_SUBMISSION{super::leapfrog::install_recipe();}std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS",&hard);std::env::set_var("PEBBLE_HARD_CAP",&hard);std::env::set_var("LF_SQUARE_CAP","1234");
 let ops:Vec<Op>=super::break_profile::load_ops(&input);let ops=super::breakthrough_generic::run(ops);super::break_profile::save_ops(&output,&ops);
}
