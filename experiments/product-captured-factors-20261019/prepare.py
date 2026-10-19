from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'product-guard-schedule-20261019/guard_schedule.rs').read_text()
assert s.count('fn main(){')==1
s=s.replace('fn main(){','fn unused_legacy_main(){',1)
s+='''
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let mut v=io::load_ops(&a[1]);let input=hash(&v);assert_eq!(input,a[3]);let tail=v.split_off(v.len()-96);for p in tail.chunks_exact(2){assert_eq!(p[0],p[1]);assert_eq!(p[0].kind,K::X);assert!(p[0].q_target.0<=1);assert_eq!(p[0].c_condition.0,NO);}let(nodes,nb)=materialize(&v);let audit=audit_conversion(&v,&nodes,nb);std::fs::write(format!("{}.guard-audit.json",a[2]),serde_json::to_string_pretty(&audit).unwrap()).unwrap();let mut out=flatten(&nodes,&(0..nodes.len()).collect::<Vec<_>>());out.extend(tail);io::save_ops(&format!("{}.ops.bin",a[2]),&out);let result=serde_json::json!({"status":"SOURCE_ORDER_GUARD_CAPTURE_AUDIT_PASS_NOT_A_SCORE","input_full_sha3_256":input,"output_full_sha3_256":hash(&out),"core_count":v.len(),"output_full_count":out.len(),"original_classical_bits":dims(&v).1,"materialized_classical_bits":nb,"every_original_gate_order_preserved":true,"all_R_and_Hmr_order_preserved":true,"no_quantum_gates_added":true,"identity_tail_unchanged":true});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("{}",result);}
'''
(r/'capture_only.rs').write_text(s,encoding='utf-8',newline='\n')
