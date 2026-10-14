"""External final-stream analysis of bit-preserving classical factor rewrites."""
from pathlib import Path
import runpy,sys
runpy.run_path(str(Path(__file__).with_name('create-factors-analysis.py')),run_name='__main__')
p=Path(sys.argv[3])/'src/main.rs';t=p.read_text().replace('classical_factors.rs','classical_factors_xor.rs').replace('mod classical_factors;','mod classical_factors_xor;').replace('classical_factors::simplify_classical','classical_factors_xor::simplify_classical');p.write_text(t,newline='\n')
