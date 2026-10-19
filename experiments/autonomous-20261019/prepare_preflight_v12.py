from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'preflight_v11.py').read_text()
needle=" ('product-classical-twelve-native-20261019','run.pid',1),";assert s.count(needle)==1
s=s.replace(needle,needle+"\n ('product-classical-twelve-native-20261019','gate.pid',3),\n ('product-classical-twelve-proof-20261019','component.pid',1),\n ('classical9-final-20261019','watch.pid',0),\n ('classical9-final-20261019','final.pid',3),")
s=s.replace("'prepare.pid':b'run-prepare.sh'","'prepare.pid':b'run-prepare.sh','component.pid':b'run-component.sh'")
(r/'preflight_v12.py').write_text(s,newline='\n')
