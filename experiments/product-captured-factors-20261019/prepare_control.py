from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'product-guard-schedule-20261019/guard_trace.rs').read_text()
s=s[:s.index('fn main()')]
s=s.replace('guard-schedule-control-physical-RNG-20261019','captured-factor-control-physical-RNG-20261019')
s+='''fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),5);let old=io::load_ops(&a[1]);let captured=io::load_ops(&a[2]);let factored=io::load_ops(&a[3]);let nb=dims(&old).1;let mut rows=vec![];let mut total_saved=0u64;
for batch in 0..8{let mut r=rng("captured-factor-control-raw-inputs-20261019",batch);let mut input=vec![];let mut seen=std::collections::BTreeSet::new();for o in &old{if o.kind==K::AppendToRegister{for(q,i)in [(true,o.q_target.0),(false,o.c_target.0)]{if i!=NO&&seen.insert((q,i)){input.push((q,i as usize,word(&mut r)));}}}}let phase=word(&mut r);let x=run(&old,batch,&input,phase);let y=run(&captured,batch,&input,phase);assert_eq!(x.0,y.0);assert_eq!(x.1,&y.1[..nb]);assert_eq!(x.2,y.2);assert_eq!(x.3,y.3);assert_eq!(x.4,y.4);let z=run(&factored,batch,&input,phase);assert_eq!(y.0,z.0);assert_eq!(y.1,z.1);assert_eq!(y.2,z.2);assert_eq!(y.4,z.4);assert!(z.3<=y.3);total_saved+=y.3-z.3;rows.push(serde_json::json!({"batch":batch,"shots":64,"all_quantum_classical_phase_and_RNG_equal":true,"old_executed_Toffolis":x.3,"factored_executed_Toffolis":z.3,"saved":x.3-z.3}));}
let report=serde_json::json!({"status":"PROTECTED_CAPTURED_CLASSICAL_FACTOR_FULL_TRANSCRIPT_CONTROL_PASS","scope":"512 raw assignments; same physical RNG; finite integration, not a curve failure gate or benchmark","original_Q":dims(&old).0,"output_Q":dims(&factored).0,"original_classical_bits":nb,"materialized_classical_bits":dims(&captured).1,"saved_executed_Toffolis_total_on_512_control_shots":total_saved,"rows":rows});std::fs::write(&a[4],serde_json::to_string_pretty(&report).unwrap()).unwrap();println!("all eight full captured-factor transcript controls pass; total saved={total_saved}");}
'''
(r/'captured_trace.rs').write_text(s,encoding='utf-8',newline='\n')
c=(r/'Cargo.toml').read_text()+'\n[[bin]]\nname="captured_factor_trace"\npath="captured_trace.rs"\n'
(r/'Cargo-control.toml').write_text(c,encoding='utf-8',newline='\n')
