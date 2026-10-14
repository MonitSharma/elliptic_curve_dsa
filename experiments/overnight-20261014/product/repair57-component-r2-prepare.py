"""Strengthen roomy complete forward/inverse fixture; preserve r1 source/results."""
from pathlib import Path
import subprocess,sys
base,out,*args=map(Path,sys.argv[1:]);subprocess.run([sys.executable,str(Path(__file__).with_name('repair57-component-prepare.py')),str(base),str(out),*map(str,args)],check=True)
s=(out/'product_repair57_tests.rs').read_text()
s=s.replace('for widths in[(56,56),(57,56),(57,57)]','for widths in[(57,56)]')
s=s.replace('let expected=q.clone();let b=vec![u64::MAX;nb];let a=kernel::audit','let expected=q.clone();for dirty in[0,u64::MAX,0xa5a5a5a5a5a5a5a5]{let b=vec![dirty;nb];let forward_a=kernel::audit(&ops[..forward],&q,&b).expect("full forward allMR");let mut correct=q.clone();hexbits(&mut correct,&ids(&abi[256..]),"d1e938360b1b3edd71badfc50840471cf63398873a042480743bffffb61167c2");assert_eq!(forward_a.qubits,correct,"independent field reference and clean forward scratch");let a=kernel::audit')
s=s.replace('let bad:Vec<_>=a.qubits.iter()', 'assert_eq!(a.qubits,expected,"full inverse allMR/allq/scratch");let bad:Vec<_>=a.qubits.iter()')
s=s.replace('Err(e)=>eprintln!("REPAIR57_BODY widths={widths:?} STRICT_ALLMR_FAILURE {e} score=NONE")','Err(e)=>panic!("REPAIR57_BODY widths={widths:?} STRICT_ALLMR_FAILURE {e} score=NONE")')
s=s.replace('sim.apply_iter(ops[forward..].iter());let wrong=', 'assert_eq!(sim.qubits,correct,"full forward native independent field reference");assert_eq!(sim.phase,0x124897da,"forward incoming phase");sim.apply_iter(ops[forward..].iter());assert_eq!(sim.qubits,expected,"full inverse native allq");assert_eq!(sim.phase,0x124897da);for i in 0..512{assert_eq!(sim.bits[i],b[i],"ABI classic slot{i}");}let wrong=')
s=s.replace('sim.stats.toffoli_gates);}});}}','sim.stats.toffoli_gates);}eprintln!("REPAIR57_STRONG_VALIDATED dirty={dirty:#x} forward_field_reference=true forward_and_inverse_ALLMR_allq_scratch_phase=true live512class=true");}});}}')
(out/'product_repair57_tests.rs').write_text(s,newline='\n')
