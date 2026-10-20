use super::*;
fn report(name:&str,ops:&[Op]){
 let(mut depth,mut native,mut weight)=(0i32,0u64,0.0f64);for o in ops{match o.kind{OperationType::PushCondition=>depth+=1,OperationType::PopCondition=>{depth-=1;assert!(depth>=0);},OperationType::CCX|OperationType::CCZ=>{native+=1;weight+=2f64.powi(-depth-i32::from(o.c_condition!=NO_BIT));},_=>{}}}assert_eq!(depth,0);let(nq,nb,_,_)=analyze_ops(ops.iter());eprintln!("TRUTH14_STAGE name={name} ops={} nq={nq} nb={nb} native={native} depth_weight={weight:.6} diagnostic_only=1",ops.len());
}
#[test]#[ignore]fn optimize_frozen_generic_stream_only_after_native_controls(){
 let input=std::env::var("TRUTH_AUDIT_INPUT").expect("Frozen input required");let prefix=std::env::var("TRUTH_AUDIT_OUTPUT").expect("New output prefix required");let mut ops=super::super::break_profile::load_ops(&input);report("input",&ops);
 ops=super::super::classical_wide::simplify_products(ops);report("products9",&ops);super::super::break_profile::save_ops(&format!("{prefix}-products9.ops.bin"),&ops);
 ops=simplify_products(ops);report("products14",&ops);super::super::break_profile::save_ops(&format!("{prefix}-products14.ops.bin"),&ops);
 ops=simplify_classical(ops);report("classical14",&ops);super::super::break_profile::save_ops(&format!("{prefix}-classical14.ops.bin"),&ops);
}
