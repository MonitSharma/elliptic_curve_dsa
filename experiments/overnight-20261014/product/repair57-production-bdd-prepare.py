"""Use unchanged validated BDD checker; never edit ANF checker or caps."""
from pathlib import Path
import subprocess,sys,hashlib
base,out,*args=map(Path,sys.argv[1:]);assert hashlib.sha256(args[2].read_bytes()).hexdigest()=='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
subprocess.run([sys.executable,str(Path(__file__).with_name('repair57-production-component-r1-prepare.py')),str(base),str(out),*map(str,args)],check=True)
s=(out/'product_repair57_tests.rs').read_text();needle='eprintln!("REPAIR57_PRODUCTION_NATIVE_VALIDATED';assert s.count(needle)==1
s=s.replace(needle,'if widths.0==57{let f=kernel::audit(&ops[..forward],&q,&b).expect("new57 exact BDD forward");assert_eq!(f.qubits,correct);let r=kernel::audit(&ops,&q,&b).expect("new57 exact BDD pair");assert_eq!(r.qubits,expected);eprintln!("REPAIR57_PRODUCTION_BDD_PROVED widths={widths:?} dirty={dirty:#x} forward_measurements={} pair_measurements={} max_forward_phase={} max_pair_phase={}",f.measurements,r.measurements,f.maximum_phase_size_bound,r.maximum_phase_size_bound); }'+needle)
(out/'product_repair57_tests.rs').write_text(s,newline='\n')
