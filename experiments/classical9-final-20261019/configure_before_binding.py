"""Configure only an unbound, unlaunched finalizer; preserve the v1 archive."""
from pathlib import Path
r=Path(__file__).resolve().parent;p=r/'audit-terminal.py';s=p.read_text()
assert s.count('UNBOUND_NOT_ACCEPTED')==2 and not (r/'watch.pid').exists()
old='Lane-0 control screened nonces 1..4096 once before launch (CONTROL.json); disclose separately, never add to the operational unique count'
new='Disabled qualification recorded24854 rows (2x128+2x11+6x4096), then operational control4096 rows:28950 repeated row attempts over unique1..4096. Production repeats from1. Seed-byte controls1,2,17,255 and nonce1 full-state replay are reference checks. Disclose separately; never add repeats to operational unique count.'
assert s.count(old)==1;s=s.replace(old,new)
p.write_text(s,newline='\n')
p=r/'run-final.sh';s=p.read_text();assert 'preflight_v11.py' in s;p.write_text(s.replace('preflight_v11.py','preflight_v13.py'),newline='\n')
print('Configured accurate preliminary accounting and current resource registry before binding')
