"""Use the same protected loader for classical factor proof analysis."""
from pathlib import Path
import runpy,sys
runpy.run_path(str(Path(__file__).with_name('create-classical-analysis.py')),run_name='__main__')
p=Path(sys.argv[3])/'src/main.rs';t=p.read_text().replace('classical_witness.rs','classical_factors.rs').replace('mod classical_witness;','mod classical_factors;').replace('classical_witness::simplify_classical','classical_factors::simplify_classical').replace('CLASSICAL_DIAGNOSTIC','FACTORS_DIAGNOSTIC');p.write_text(t,newline='\n')
