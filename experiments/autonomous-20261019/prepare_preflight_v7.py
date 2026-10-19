from pathlib import Path
r=Path(__file__).resolve().parent
p=r/'preflight_v6.py';s=p.read_text()
needle=" ('product-classical-nine-20261019','run.pid',1),"
assert s.count(needle)==1
(r/'preflight_v7.py').write_text(s.replace(needle,needle+"\n ('product-classical-nine-proof-20261019','run.pid',1),"))
p=r.parent/'product-classical-nine-20261019/run-gate.sh'
s=p.read_text();p.write_text(s.replace('preflight_v6','preflight_v7'))
