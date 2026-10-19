"""Keep the same protected physical-RNG control, extended for fresh bits."""
from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'product-order-20261019/trace-tool/trace.rs').read_text()
s=s[:s.index('fn main()')]
s=s.replace('#[path="../io.rs"]mod io;','mod io;')
s=s.replace('order-control-physical-RNG-20261019','guard-schedule-control-physical-RNG-20261019')
s+='''fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),6);
 let original=io::load_ops(&a[1]);let converted=io::load_ops(&a[2]);let ordered=io::load_ops(&a[3]);let colored=io::load_ops(&a[4]);let old_nb=dims(&original).1;
 let registered:std::collections::BTreeSet<_>=original.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=NO).map(|o|o.q_target.0 as usize).collect();let mut rows=vec![];
 for batch in 0..8{let mut r=rng("guard-schedule-control-uniform-raw-inputs-20261019",batch);let mut input=vec![];let mut seen=std::collections::BTreeSet::new();for o in &original{if o.kind==K::AppendToRegister{for(q,i)in [(true,o.q_target.0),(false,o.c_target.0)]{if i!=NO&&seen.insert((q,i)){input.push((q,i as usize,word(&mut r)));}}}}let phase=word(&mut r);
  let x=run(&original,batch,&input,phase);let y=run(&converted,batch,&input,phase);assert_eq!(x.0,y.0,"all original quantum wires after materialization");assert_eq!(x.1,&y.1[..old_nb],"all original classical bits after materialization");assert_eq!(x.2,y.2,"phase after materialization");assert_eq!(x.3,y.3,"executed Toffolis after materialization");assert_eq!(x.4,y.4,"physical RNG continuation after materialization");
  let z=run(&ordered,batch,&input,phase);assert_eq!(y,z,"all quantum/classical (including fresh bits), phase, cost and physical RNG after scheduling");let w=run(&colored,batch,&input,phase);assert_eq!(z.1,w.1,"allocator classical bits including captured predicates");assert_eq!(z.2,w.2,"allocator phase");assert_eq!(z.3,w.3,"allocator executed Toffolis");assert_eq!(z.4,w.4,"allocator physical RNG continuation");for &q in &registered{assert_eq!(z.0[q],w.0[q],"registered quantum output");}
  let scratch=|v:&Vec<u64>|{let mut out:Vec<_>=v.iter().enumerate().filter(|(q,_)|!registered.contains(q)).map(|(_,x)|*x).collect();out.resize(dims(&original).0-registered.len(),0);out.sort_unstable();out};assert_eq!(scratch(&z.0),scratch(&w.0),"scratch-state multiset");rows.push(serde_json::json!({"batch":batch,"shots":64,"all_original_values_phase_cost_and_physical_RNG_equal_after_materialization":true,"all_values_including_fresh_classical_bits_equal_after_reordering":true,"colored_outputs_bits_phase_cost_RNG_and_scratch_equal":true}));
 }
 let result=serde_json::json!({"status":"PROTECTED_SIMULATOR_MATERIALIZED_GUARD_PHYSICAL_TRANSCRIPT_CONTROL_PASS","scope":"512 uniformly sampled raw assignments and arbitrary initial phase; tool integration, not a curve failure-rate gate or score","original_Q":dims(&original).0,"colored_Q":dims(&colored).0,"original_classical_bits":old_nb,"materialized_classical_bits":dims(&ordered).1,"rows":rows});std::fs::write(&a[5],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("all eight full materialized-guard physical-RNG transcript controls pass");
}
'''
(r/'guard_trace.rs').write_text(s,encoding='utf-8',newline='\n')
cargo=(r/'Cargo.toml').read_text()
assert 'name="guard_trace"' not in cargo
cargo+='\n[[bin]]\nname="guard_trace"\npath="guard_trace.rs"\n'
(r/'Cargo-control.toml').write_text(cargo,encoding='utf-8',newline='\n')
