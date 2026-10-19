import subprocess,sys,json
from pathlib import Path
r=Path(__file__).resolve().parent
runtime=Path('/home/hclau/tools/miniforge3/bin/python')
assert runtime.exists()
assert not (r/'libraries').exists()
subprocess.run([str(runtime),'-m','pip','install','--no-cache-dir','--disable-pip-version-check',
                '--target',str(r/'libraries'),'z3-solver==5.1.0.0'],check=True)
sys.path.insert(0,str(r/'libraries'));import z3
(r/'SOLVER.json').write_text(json.dumps({'python':str(runtime),'z3_version':z3.get_version_string()},indent=2)+'\n')
print(z3.get_version_string())
