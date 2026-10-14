"""Prove a conditional CCX toggle factors through a live classical bit."""
from pathlib import Path
import sys
s=Path(sys.argv[1]);t=(s/'classical_witness.rs').read_text()
t=t.replace('let mut out=Vec::with_capacity(ops.len());let mut hits=0;let mut proxy=0.;let mut depth=0;',
'''let mut by_atom:HashMap<u64,BTreeSet<usize>>=HashMap::new();
 for (b,v) in state.bits.iter().enumerate(){for &a in &v.atoms{by_atom.entry(a).or_default().insert(b);}}
 let mut out=Vec::with_capacity(ops.len());let mut hits=0;let mut complement_hits=0;let mut proxy=0.;let mut depth=0;let mut fresh_bit=state.bits.len() as u64;''')
old='''  let witness=if o.kind==OperationType::CCX {
   [(o.q_control1,o.q_control2),(o.q_control2,o.q_control1)].into_iter().find_map(|(q,other)|
    index.get(&state.qubits[q.0 as usize]).and_then(|slots|slots.first().copied()).map(|b|(b,other)))
  }else{None};'''
new='''  let witness=if o.kind==OperationType::CCX {
   let mut found=[(o.q_control1,o.q_control2),(o.q_control2,o.q_control1)].into_iter().find_map(|(q,other)|
    index.get(&state.qubits[q.0 as usize]).and_then(|slots|slots.first().copied()).map(|b|(b,other,false)));
   if found.is_none(){
    let a=state.qubits[o.q_control1.0 as usize].clone();let b=state.qubits[o.q_control2.0 as usize].clone();
    let mut condition=state.base_condition.clone();
    if o.c_condition!=NO_BIT{condition=state.and(&condition,&state.bits[o.c_condition.0 as usize].clone());}
    let product=state.and(&a,&b);let effective=state.and(&condition,&product);
    let candidates:BTreeSet<usize>=a.atoms.iter().chain(&b.atoms).chain(&condition.atoms).filter_map(|a|by_atom.get(a)).flat_map(|s|s.iter().copied()).collect();
    'search:for bit in candidates{
     let value=state.bits[bit].clone();
     for negated in [false,true]{let classical=if negated{value.complement()}else{value.clone()};
      for (wire,v) in [(o.q_control1,&a),(o.q_control2,&b)]{
       let controlled=state.and(&condition,v);let factored=state.and(&controlled,&classical);
       if factored==effective{found=Some((bit,wire,negated));break 'search;}
      }
     }
    }
   }
   found
  }else{None};'''
assert t.count(old)==1;t=t.replace(old,new)
t=t.replace('if let Some(b)=changed{let old=&state.bits[b];',
'''if let Some(b)=changed{let old=&state.bits[b];for a in &old.atoms{if let Some(slots)=by_atom.get_mut(a){slots.remove(&b);if slots.is_empty(){by_atom.remove(a);}}}''')
t=t.replace('if let Some(b)=changed{let v=&state.bits[b];if',
'''if let Some(b)=changed{let v=&state.bits[b];for &a in &v.atoms{by_atom.entry(a).or_default().insert(b);}if''')
t=t.replace('if let Some((b,other))=witness{',
'''if let Some((b,other,negated))=witness{
   let bit=if negated{
    // A new unscored bit stores the complement; never mutate the witness or
    // the original operation's own condition. Outer stack snapshots persist.
    let dst=crate::circuit::BitId(fresh_bit);fresh_bit+=1;
    let mut one=Op::empty();one.kind=OperationType::BitStore1;one.c_target=dst;
    let mut flip=Op::empty();flip.kind=OperationType::BitInvert;flip.c_target=dst;flip.c_condition=crate::circuit::BitId(b as u64);
    out.extend([one,flip]);complement_hits+=1;dst
   }else{crate::circuit::BitId(b as u64)};''')
t=t.replace('push.c_condition=crate::circuit::BitId(b as u64);','push.c_condition=bit;')
t=t.replace('CLASSICAL_WITNESS native_hits={hits}', 'CLASSICAL_FACTORS native_hits={hits} complement_hits={complement_hits}')
t=t.replace('tests_classical_witness.rs','tests_classical_factors.rs')
(s/'classical_factors.rs').write_text(t,newline='\n')
tests=(s/'tests_classical_witness.rs').read_text()
# Complement support means mutable-bit test can now repair through !bit.
tests=tests.replace('count(),1);paired(&ops,&out);','count(),0);paired(&ops,&out);')
tests+='''
#[test]fn quantum_control_product_has_a_classical_factor(){
 for complement in [false,true]{for same_condition in [false,true]{
  let mut ops=fixture();ops.extend(copy(0,1));
  let mut cx=Op::empty();cx.kind=OperationType::CX;cx.q_control1=QubitId(0);cx.q_target=QubitId(1);ops.push(cx);
  if !complement{let mut x=Op::empty();x.kind=OperationType::X;x.q_target=QubitId(1);ops.push(x);}
  let mut gate=ccx();if same_condition{gate.c_condition=BitId(0);}ops.push(gate);
  let out=simplify_classical(ops.clone());assert_eq!(out.iter().filter(|o|o.kind==OperationType::CCX).count(),0);
  paired(&ops,&out);
 }}
}
'''
(s/'tests_classical_factors.rs').write_text(tests,newline='\n')
