"""Inspect conservative exact ANF-zero facts at the coordinator's peak op."""
from pathlib import Path
import runpy,sys
candidate=Path(sys.argv[2]);dest=Path(sys.argv[3])
t=(candidate/'bounded_anf.rs').read_text()
t+='''
pub(crate) fn audit_zero(ops:&[Op],at:usize)->Vec<usize>{
 let mut s=Support::new(ops);
 for o in ops.iter().take(at){s.step(o);}
 s.qubits.iter().enumerate().filter_map(|(q,v)|v.is_zero().then_some(q)).collect()
}
'''
(candidate/'bounded_anf_peak.rs').write_text(t,newline='\n')
runpy.run_path(str(Path(__file__).with_name('create-anf-analysis.py')),run_name='__main__')
p=dest/'src/main.rs';t=p.read_text().replace('bounded_anf.rs','bounded_anf_peak.rs').replace('mod bounded_anf;','mod bounded_anf_peak;')
t=t.replace('bounded_anf::simplify(ops)','{let known=bounded_anf_peak::audit_zero(&ops,1444991);eprintln!("ANF_PEAK_ZERO before_op1444991 known_zero={known:?}");ops}')
p.write_text(t,newline='\n')
