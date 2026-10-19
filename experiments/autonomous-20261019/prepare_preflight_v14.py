"""Leave every live bound profile unchanged; extend a new explicit registry."""
from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'preflight_v13.py').read_text()
s=s.replace("['parent4-operational-sat-20261019','product-classical-nine-operational-20261019']","['parent4-operational-sat-20261019','product-classical-nine-operational-20261019','product-classical-twelve-operational-20261019']")
needle=" ('product-classical-twelve-proof-20261019','run.pid',1),";assert s.count(needle)==1
s=s.replace(needle,needle+"\n ('product-classical-twelve-filter-20261019','build.pid',1),\n ('product-classical-twelve-filter-20261019','watch.pid',0),\n ('product-classical-twelve-filter-20261019','qualification.pid',3),\n ('product-classical-twelve-operational-20261019','prepare.pid',1),\n ('product-classical-twelve-operational-20261019','control.pid',3),\n ('classical9-final-v2-20261019','watch.pid',0),\n ('classical9-final-v2-20261019','final.pid',3),")
s=s.replace("if directory=='product-classical-nine-filter-20261019' and pidfile=='watch.pid'", "if directory in ['product-classical-nine-filter-20261019','product-classical-twelve-filter-20261019'] and pidfile=='watch.pid'")
p=r/'preflight_v14.py';assert not p.exists();p.write_text(s,newline='\n')
