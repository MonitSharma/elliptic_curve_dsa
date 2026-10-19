import gzip,hashlib,json,sys,time
from pathlib import Path
r=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'libraries'))
import z3
p=Path(sys.argv[1]);solver=z3.Solver();solver.set(timeout=180000)
solver.from_string(gzip.open(p,'rt').read())
t=time.monotonic();v=solver.check()
d={'verdict':str(v),'seconds':time.monotonic()-t,'formula_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'z3_version':z3.get_version_string()}
Path(sys.argv[2]).write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d),flush=True)
assert v==z3.unsat,'Formula replay was not UNSAT; qualification remains disabled'
