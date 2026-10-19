from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'preflight_v7.py').read_text()
needle=" ('product-classical-nine-20261019','gate.pid',3),"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n ('product-classical-nine-20261019','gate-v2.pid',3),")
s=s.replace("'gate.pid':b'run-gate.sh'","'gate.pid':b'run-gate.sh','gate-v2.pid':b'run-gate-v2.sh'")
(r/'preflight_v8.py').write_text(s,newline='\n')
