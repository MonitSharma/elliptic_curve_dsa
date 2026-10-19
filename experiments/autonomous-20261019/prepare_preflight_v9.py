from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'preflight_v8.py').read_text()
needle=" ('product-classical-nine-20261019','gate-v2.pid',3),";assert s.count(needle)==1
s=s.replace(needle,needle+"\n ('product-classical-nine-filter-20261019','build.pid',1),\n ('product-classical-nine-filter-20261019','watch.pid',0),\n ('product-classical-nine-filter-20261019','qualification.pid',3),")
needle="if expected not in command:continue";assert s.count(needle)==1
s=s.replace(needle,"if directory=='product-classical-nine-filter-20261019' and pidfile=='watch.pid':expected=b'after_gate.py'\n    "+needle)
s=s.replace("'gate-v2.pid':b'run-gate-v2.sh'","'gate-v2.pid':b'run-gate-v2.sh','build.pid':b'run-build.sh','qualification.pid':b'run-qualify.sh'")
(r/'preflight_v9.py').write_text(s,newline='\n')
