"""Finite actual-prefix all-future-MR proof on two exact producer/fold slices."""
from pathlib import Path
import subprocess,sys
base,dest,archive,kernel_path=map(Path,sys.argv[1:5])
subprocess.run([sys.executable,str(Path(__file__).with_name('fold75-prepare-replay.py')),str(base),str(dest),str(archive)],check=True)
(dest/'src/fold75_kernel.rs').write_bytes(kernel_path.read_bytes())
s=(dest/'src/main.rs').read_text().replace('mod y33_copy;','mod y33_copy;\nmod fold75_kernel;')
needle='    let mut final_at=0usize;let mut logical=';assert s.count(needle)==1
s=s.replace(needle,'    let mut detail:Option<fold75_kernel::Diagnosis>=None;\n'+needle)
at=s.index('    for(lane,(index,_))in cases.iter().enumerate(){if mode=="independent"')
hook=r'''
    if frame.label=="before-fold-producer"{
      assert!(logical.is_empty());let end=frames[seq+1].end;assert_eq!(frames[seq+1].label,"after-fold-producer");assert!(sites.iter().all(|s|!(s.1[0]<end&&s.2>=end)),"endpoint no pending Y33 ensures exact original/final indices");
      match fold75_kernel::diagnose(&ops[final_at..end],&sim.qubits,&sim.bits){Ok(d)=>{let active=if cases.len()==64{u64::MAX}else{(1u64<<cases.len())-1};let phase_lanes=d.phase_terms.iter().fold(0u64,|v,(_,c)|v|c)&active;
       let target_constant=frame.p[0].iter().all(|&q|d.qubits[q].is_some());eprintln!("FOLD75_ALLMR source={source} mode={mode} batch={batch} tick={} start={final_at} end={end} ops={} cases={} measurements={} nonconstant_q={} target_constant={target_constant} phase_terms={} nonzero_phase_lanes={phase_lanes:#x} max_phase={} max_q={} score=NONE",frame.t,end-final_at,cases.len(),d.measurements,d.qubits.iter().filter(|v|v.is_none()).count(),d.phase_terms.len(),d.maximum_phase_terms,d.maximum_quantum_terms);
       for(ids,coefficient)in &d.phase_terms{if coefficient&active!=0{eprintln!("FOLD75_PHASE_TERM source={source} mode={mode} batch={batch} tick={} ids={ids:?} coefficient={:#x}",frame.t,coefficient&active);}}detail=Some(d);
      },Err(e)=>{eprintln!("FOLD75_INCONCLUSIVE source={source} mode={mode} batch={batch} tick={} {e}",frame.t);panic!("audit inconclusive retained without phase/value interpretation");}}
    }else if frame.label=="after-fold-producer"{
      let d=detail.take().unwrap();assert_eq!(d.qubits.len(),sim.qubits.len());let mut constant=0;for(q,v)in d.qubits.iter().enumerate(){if let Some(v)=v{assert_eq!(*v,sim.qubits[q],"allMR output constant differs from original native whole-prefix transcript");constant+=1;}}
      eprintln!("FOLD75_NATIVE_CONSTANT_CHECK source={source} mode={mode} batch={batch} tick={} exact_constant_quantum_slots={constant} original_prefix_same=true score=NONE",frame.t);
    }
'''
s=s[:at]+hook+s[at:]
s=s.replace('PRODUCT_FOLD_','PRODUCT_FOLD75_ALLMR_')
(dest/'src/main.rs').write_text(s,newline='\n')
