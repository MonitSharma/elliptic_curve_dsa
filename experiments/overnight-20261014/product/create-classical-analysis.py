"""Use the protected loader for a classical control witness analysis."""
from pathlib import Path
import runpy,sys
runpy.run_path(str(Path(__file__).with_name('create-anf-analysis.py')),run_name='__main__')
dest=Path(sys.argv[3]);candidate=Path(sys.argv[2]);p=dest/'src/main.rs';t=p.read_text()
t=t.replace('bounded_anf.rs','classical_witness.rs').replace('bounded_anf','classical_witness')
t=t.replace('classical_witness::simplify(ops)','classical_witness::simplify_classical(ops)')
needle='mod affine_simplify;'
t=t.replace(needle,needle+f'\n #[path="{(candidate/"quadratic_simplify.rs").as_posix()}"] mod quadratic_simplify;')
t=t.replace('ANF_DIAGNOSTIC','CLASSICAL_DIAGNOSTIC');p.write_text(t,newline='\n')
