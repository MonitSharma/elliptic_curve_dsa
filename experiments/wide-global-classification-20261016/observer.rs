static OBSERVE_AT:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
fn observe_global(condition:&Affine,a:&Affine,b:&Affine,op:&Op,rewrite:&Rewrite,depth:usize){
 if matches!(rewrite,Rewrite::Keep){return;}
 let reason=if condition.is_zero(){"execution_condition_proved_zero"}else if a.is_zero()||b.is_zero(){"quantum_control_proved_zero"}else if a.complements(b){"complementary_quantum_controls"}else if a.is_one()&&b.is_one(){"both_quantum_controls_one"}else if a.is_one()||b.is_one(){"one_quantum_control_one"}else if a==b{"equal_quantum_control_functions"}else{panic!("unclassified global rewrite")};
 let replacement=match rewrite{Rewrite::Keep=>unreachable!(),Rewrite::Drop=>"Drop",Rewrite::X=>"X",Rewrite::Cx(_)=>"CX"};
 let form=|x:&Affine|serde_json::json!({"constant":x.constant,"atoms":x.atoms});
 println!("{}",serde_json::json!({"op":OBSERVE_AT.load(std::sync::atomic::Ordering::Relaxed),"target":op.q_target.0,"controls":[op.q_control1.0,op.q_control2.0],"direct_condition":if op.c_condition==NO_BIT{None}else{Some(op.c_condition.0)},"guard_depth":depth,"syntactic_weight_exponent":depth+usize::from(op.c_condition!=NO_BIT),"guard_status":if condition.is_zero(){"identically_zero"}else if condition.is_one(){"identically_one"}else{"nonconstant_symbolic"},"reason":reason,"replacement":replacement,"condition_form":form(condition),"control_forms":[form(a),form(b)]}));
}
pub(crate) fn run_global_classification(ops:&[Op]){let mut state=Support::new(ops);for(at,op)in ops.iter().enumerate(){OBSERVE_AT.store(at,std::sync::atomic::Ordering::Relaxed);let _=state.step(op);}}
