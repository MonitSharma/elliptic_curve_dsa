"""Copied strict kernel plus separate detailed all-MR finite-context diagnostic."""
from pathlib import Path
import subprocess,sys
base,dest,archive,kernel_path=map(Path,sys.argv[1:5])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-walk-replay.py')),str(base),str(dest),str(archive)],check=True)
kernel=kernel_path.read_text()
start=kernel.index('pub fn audit(');end=kernel.index('\n#[cfg(test)]',start)
detail=kernel[start:end].replace('pub fn audit(','pub fn diagnose(',1).replace('Result<Audit, String>', 'Result<Diagnosis, String>',1)
needle='''    if !phase.0.is_empty() {
        return Err(format!("nonzero phase polynomial: {} terms; first {:?}", phase.0.len(), phase.0.first_key_value()));
    }
''';assert detail.count(needle)==1;detail=detail.replace(needle,'')
detail=detail.replace('output.push(value.scalar().ok_or_else(|| format!("measurement-dependent final quantum slot {slot}"))?);','output.push(value.scalar());')
detail=detail.replace('Ok(Audit { qubits: output,','Ok(Diagnosis { phase_terms:phase.0.into_iter().collect(),qubits: output,')
addition=r'''
#[derive(Debug)]pub struct Diagnosis{pub qubits:Vec<Option<u64>>,pub measurements:u64,pub phase_terms:Vec<(Vec<u32>,u64)>,pub maximum_phase_terms:usize,pub maximum_quantum_terms:usize}
'''+detail+r'''
#[cfg(test)]mod detail_tests{use super::*;use crate::circuit::{QubitId,BitId};
 #[test]fn detailed_phase_and_measurement_dependent_value_fault(){
  let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(0);h.c_target=BitId(0);
  let mut x=Op::empty();x.kind=K::X;x.q_target=QubitId(1);x.c_condition=BitId(0);
  let ops=[h,x];let d=diagnose(&ops,&[u64::MAX,u64::MAX],&[]).unwrap();assert_eq!(d.qubits,vec![Some(0),None]);assert_eq!(d.phase_terms,vec![(vec![0],u64::MAX)]);
  struct Reader{word:u64}impl sha3::digest::XofReader for Reader{fn read(&mut self,b:&mut[u8]){assert_eq!(b.len(),8);b.copy_from_slice(&self.word.to_le_bytes());}}
  for m in [0,u64::MAX,0xa5a5a5a5a5a5a5a5]{let mut reader=Reader{word:m};let mut sim=quantum_ecc::sim::Simulator::new(2,1,&mut reader);sim.qubits=vec![u64::MAX,u64::MAX];sim.apply_iter(ops.iter());assert_eq!(sim.qubits,vec![0,!m]);assert_eq!(sim.phase,m);let evaluated=d.phase_terms.iter().fold(0u64,|v,(ids,coef)|v^(if ids==&vec![0]{m&coef}else{panic!("unexpected monomial")}));assert_eq!(evaluated,sim.phase);}
 }
}
'''
(dest/'src/rail109_kernel.rs').write_text(kernel+'\n'+addition,newline='\n')
s=(dest/'src/main.rs').read_text().replace('mod y33_copy;','mod y33_copy;\nmod rail109_kernel;')
needle='    let mut final_at=0usize;let mut logical='
assert s.count(needle)==1
s=s.replace(needle,'    let mut detail:Option<rail109_kernel::Diagnosis>=None;\n'+needle)
at=s.index('    for(lane,(index,_))in cases.iter().enumerate(){if mode=="independent"')
hook=r'''
    if mode=="official_known_bad"&&frame.scope=="mul"&&frame.t==109{
      if frame.label=="fwd_tick_before"{assert!(logical.is_empty());let end=frames[seq+1].end;assert_eq!(frames[seq+1].label,"fwd_tick_after");assert_eq!(end,ops.iter().take(end).count());let diagnosis=rail109_kernel::diagnose(&ops[final_at..end],&sim.qubits,&sim.bits);match diagnosis{Ok(d)=>{let active=(1u64<<cases.len())-1;let phase_lanes=d.phase_terms.iter().fold(0u64,|v,(_,c)|v|c)&active;eprintln!("RAIL109_ALLMR source={source} start={final_at} end={end} ops={} cases={} measurements={} nonconstant_q={} phase_terms={} nonzero_phase_lanes={phase_lanes:#x} max_phase={} max_q={} score=NONE",end-final_at,cases.len(),d.measurements,d.qubits.iter().filter(|v|v.is_none()).count(),d.phase_terms.len(),d.maximum_phase_terms,d.maximum_quantum_terms);for(ids,coefficient)in &d.phase_terms{if coefficient&active!=0{eprintln!("RAIL109_PHASE_TERM source={source} ids={ids:?} coefficient={:#x}",coefficient&active);}}detail=Some(d);},Err(e)=>{eprintln!("RAIL109_INCONCLUSIVE source={source} {e}");panic!("audit inconclusive retained without phase/value interpretation");}}}
      else if frame.label=="fwd_tick_after"{let d=detail.take().unwrap();assert_eq!(d.qubits.len(),sim.qubits.len());let mut constant=0;for(q,v)in d.qubits.iter().enumerate(){if let Some(v)=v{assert_eq!(*v,sim.qubits[q],"allMR output constant differs from original native whole-prefix transcript");constant+=1;}}eprintln!("RAIL109_NATIVE_CONSTANT_CHECK source={source} exact_constant_quantum_slots={constant} original_prefix_same=true score=NONE");}
    }
'''
s=s[:at]+hook+s[at:]
s=s.replace('PRODUCT_WALK_','PRODUCT_RAIL109_')
(dest/'src/main.rs').write_text(s,newline='\n')
