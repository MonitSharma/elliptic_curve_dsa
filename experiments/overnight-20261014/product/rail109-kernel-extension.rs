

#[derive(Debug)]pub struct Diagnosis{pub qubits:Vec<Option<u64>>,pub measurements:u64,pub phase_terms:Vec<(Vec<u32>,u64)>,pub maximum_phase_terms:usize,pub maximum_quantum_terms:usize}
pub fn diagnose(ops: &[Op], input: &[u64], initial_bits: &[u64]) -> Result<Diagnosis, String> {
    let (nq, nb, _, _) = analyze_ops(ops.iter());
    if input.len() < nq as usize { return Err("input shorter than quantum allocation".into()); }
    let mut q: Vec<_> = input.iter().map(|v| Poly::constant(*v)).collect();
    let mut bits = vec![Poly::constant(0); (nb as usize).max(initial_bits.len())];
    for (bit, value) in initial_bits.iter().enumerate() { bits[bit] = Poly::constant(*value); }
    let mut phase = Poly::constant(0);
    let mut base = Poly::constant(u64::MAX);
    let mut stack = Vec::new();
    let mut next_measurement = 0u32;
    let (mut max_phase, mut max_quantum) = (0, 1);
    for (index, op) in ops.iter().enumerate() {
        let condition = if op.c_condition == NO_BIT { base.clone() }
            else { base.and(&bits[op.c_condition.0 as usize])? };
        let (a, b, t, bit) = (op.q_control1.0 as usize, op.q_control2.0 as usize,
                             op.q_target.0 as usize, op.c_target.0 as usize);
        match op.kind {
            K::PushCondition => { stack.push(base); base = condition; }
            K::PopCondition => { base = stack.pop().ok_or_else(|| format!("unbalanced pop at {index}"))?; }
            K::X => { q[t] = q[t].xor(&condition)?; }
            K::CX => { q[t] = q[t].xor(&condition.and(&q[a])?)?; }
            K::CCX => { q[t] = q[t].xor(&condition.and(&q[a].and(&q[b])?)?)?; }
            K::Swap => {
                let delta = condition.and(&q[a].xor(&q[t])?)?;
                q[a] = q[a].xor(&delta)?; q[t] = q[t].xor(&delta)?;
            }
            K::R | K::Hmr => {
                let m = Poly::variable(next_measurement);
                next_measurement = next_measurement.checked_add(1).ok_or("measurement id overflow")?;
                phase = phase.xor(&condition.and(&q[t].and(&m)?)?)?;
                if op.kind == K::Hmr {
                    bits[bit] = bits[bit].xor(&condition.and(&bits[bit].xor(&m)?)?)?;
                }
                q[t] = q[t].and(&condition.not()?)?;
            }
            K::BitInvert => { bits[bit] = bits[bit].xor(&condition)?; }
            K::BitStore0 => { bits[bit] = bits[bit].and(&condition.not()?)?; }
            K::BitStore1 => { bits[bit] = bits[bit].xor(&condition.and(&bits[bit].not()?)?)?; }
            K::Neg => { phase = phase.xor(&condition)?; }
            K::Z => { phase = phase.xor(&condition.and(&q[t])?)?; }
            K::CZ => { phase = phase.xor(&condition.and(&q[a].and(&q[t])?)?)?; }
            K::CCZ => { phase = phase.xor(&condition.and(&q[a].and(&q[b].and(&q[t])?)?)?)?; }
            K::Register | K::AppendToRegister | K::DebugPrint => {}
        }
        max_phase = max_phase.max(phase.0.len());
        match op.kind {
            K::X | K::CX | K::CCX | K::R | K::Hmr => { max_quantum = max_quantum.max(q[t].0.len()); }
            K::Swap => { max_quantum = max_quantum.max(q[t].0.len()).max(q[a].0.len()); }
            _ => {}
        }
    }
    if !stack.is_empty() { return Err("unclosed condition stack".into()); }
    let mut output = Vec::with_capacity(q.len());
    for (slot, value) in q.iter().enumerate() {
        output.push(value.scalar());
    }
    Ok(Diagnosis { phase_terms:phase.0.into_iter().collect(),qubits: output, measurements: next_measurement as u64,
               maximum_phase_terms: max_phase, maximum_quantum_terms: max_quantum })
}

#[cfg(test)]mod detail_tests{use super::*;use crate::circuit::{QubitId,BitId};
 #[test]fn detailed_phase_and_measurement_dependent_value_fault(){
  let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(0);h.c_target=BitId(0);
  let mut x=Op::empty();x.kind=K::X;x.q_target=QubitId(1);x.c_condition=BitId(0);
  let ops=[h,x];let d=diagnose(&ops,&[u64::MAX,u64::MAX],&[]).unwrap();assert_eq!(d.qubits,vec![Some(0),None]);assert_eq!(d.phase_terms,vec![(vec![0],u64::MAX)]);
  struct Reader{word:u64}impl sha3::digest::XofReader for Reader{fn read(&mut self,b:&mut[u8]){assert_eq!(b.len(),8);b.copy_from_slice(&self.word.to_le_bytes());}}
  for m in [0,u64::MAX,0xa5a5a5a5a5a5a5a5]{let mut reader=Reader{word:m};let mut sim=quantum_ecc::sim::Simulator::new(2,1,&mut reader);sim.qubits=vec![u64::MAX,u64::MAX];sim.apply_iter(ops.iter());assert_eq!(sim.qubits,vec![0,!m]);assert_eq!(sim.phase,m);let evaluated=d.phase_terms.iter().fold(0u64,|v,(ids,coef)|v^(if ids==&vec![0]{m&coef}else{panic!("unexpected monomial")}));assert_eq!(evaluated,sim.phase);}
 }
}
