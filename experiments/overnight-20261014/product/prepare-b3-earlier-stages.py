"""Versioned raw/pre-Y42 observation; retains all prior stage and binding checks."""
from pathlib import Path
import subprocess, sys
base, output, evidence=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-b3-stages.py')),str(base),str(output),str(evidence)],check=True)
p=output/'mod.rs';s=p.read_text()
needle='    let mut ops = build_point_add();'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n    product_b3_stage_observer::save(&ops,"raw-body");')
needle='    ops = y42_bound_pass::run(ops);'
assert s.count(needle)==1
s=s.replace(needle,'    product_b3_stage_observer::save(&ops,"before-y42-bound");\n'+needle)
p.write_text(s,newline='\n')
