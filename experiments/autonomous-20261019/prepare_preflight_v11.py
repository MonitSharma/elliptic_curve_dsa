from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'preflight_v10.py').read_text()
needle=" ('product-classical-nine-operational-20261019','prepare.pid',1),";assert s.count(needle)==1
s=s.replace(needle,needle+"\n ('product-classical-twelve-native-20261019','run.pid',1),\n ('product-classical-twelve-proof-20261019','run.pid',1),")
(r/'preflight_v11.py').write_text(s,newline='\n')
