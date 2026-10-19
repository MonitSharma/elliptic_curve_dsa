from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'preflight_v9.py').read_text()
needle=" ('product-classical-nine-filter-20261019','qualification.pid',3),";assert s.count(needle)==1
s=s.replace(needle,needle+"\n ('product-classical-factors-wide-20261019','run-v2.pid',1),\n ('product-classical-nine-operational-20261019','prepare.pid',1),\n ('product-classical-nine-operational-20261019','control.pid',3),")
s=s.replace("'qualification.pid':b'run-qualify.sh'","'qualification.pid':b'run-qualify.sh','run-v2.pid':b'run-v2.sh','prepare.pid':b'run-prepare.sh'")
(r/'preflight_v10.py').write_text(s,newline='\n')
