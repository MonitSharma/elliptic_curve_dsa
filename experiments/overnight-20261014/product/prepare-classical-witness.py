"""Add exact current-classical-slot witnesses to the seven-atom interpreter."""
from pathlib import Path
import sys
s=Path(sys.argv[1]);t=(s/'truth7_simplify.rs').read_text()
t=t[:t.index('\n#[cfg(test)]')]
t+='''
/// Exact positive control witnesses. Classical bits already contain their
/// values, so no quantum measurement/coherence is changed by conditioning.
pub(crate) fn simplify_classical(ops:Vec<Op>)->Vec<Op>{
 use std::collections::{HashMap,BTreeSet};
 let mut state=Support::new(&ops);let mut index:HashMap<Truth,BTreeSet<usize>>=HashMap::new();
 for (b,v) in state.bits.iter().enumerate(){if !v.is_zero()&&!v.is_one(){index.entry(v.clone()).or_default().insert(b);}}
 let mut out=Vec::with_capacity(ops.len());let mut hits=0;let mut proxy=0.;let mut depth=0;
 for o in ops{
  if o.kind==OperationType::PushCondition{depth+=1;}if o.kind==OperationType::PopCondition{depth-=1;}
  let witness=if o.kind==OperationType::CCX {
   [(o.q_control1,o.q_control2),(o.q_control2,o.q_control1)].into_iter().find_map(|(q,other)|
    index.get(&state.qubits[q.0 as usize]).and_then(|slots|slots.first().copied()).map(|b|(b,other)))
  }else{None};
  let changed=match o.kind{OperationType::Hmr|OperationType::BitInvert|OperationType::BitStore0|OperationType::BitStore1=>Some(o.c_target.0 as usize),_=>None};
  if let Some(b)=changed{let old=&state.bits[b];if let Some(slots)=index.get_mut(old){slots.remove(&b);if slots.is_empty(){index.remove(old);}}}
  state.step(&o);
  if let Some(b)=changed{let v=&state.bits[b];if !v.is_zero()&&!v.is_one(){index.entry(v.clone()).or_default().insert(b);}}
  if let Some((b,other))=witness{
   let mut push=Op::empty();push.kind=OperationType::PushCondition;push.c_condition=crate::circuit::BitId(b as u64);
   let mut gate=Op::empty();gate.kind=OperationType::CX;gate.q_control1=other;gate.q_target=o.q_target;gate.c_condition=o.c_condition;gate.validate();
   let mut pop=Op::empty();pop.kind=OperationType::PopCondition;
   out.extend([push,gate,pop]);hits+=1;proxy+=2f64.powi(-depth-i32::from(o.c_condition!=NO_BIT));
  }else{out.push(o);}
 }
 eprintln!("CLASSICAL_WITNESS native_hits={hits} condition_depth_proxy_saving={proxy} measurements_added=0 quantum_scratch_added=0");
 out
}
#[cfg(test)] #[path="tests_classical_witness.rs"] mod tests;
'''
(s/'classical_witness.rs').write_text(t,newline='\n')
