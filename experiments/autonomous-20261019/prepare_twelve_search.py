"""Prepare unchanged ascending dispatch with source12 qualification bindings."""
from pathlib import Path
import json
ws=Path(__file__).resolve().parent.parent;old=ws/'product-classical-nine-operational-20261019';r=ws/'product-classical-twelve-operational-20261019'
assert not (r/'search.pid').exists()
for name in ['launch_search.py','preflight_search.py','run-search.sh','refresh_record.py']:
 s=(old/name).read_text()
 for a,b in [('parent4-operational-sat-20261019','product-classical-nine-operational-20261019'),('classical9-final-20261019','classical12-final-20261020'),('CLASSICAL9','CLASSICAL12'),('preflight_v13.py','preflight_v15.py'),('parent4-retirement-20261019','classical9-retirement-20261020')]:s=s.replace(a,b)
 # Old root references in launch policy above are intentional; replace the new job's own shell and display names only.
 if name=='run-search.sh':s=s.replace('product-classical-nine-operational-20261019','product-classical-twelve-operational-20261019')
 if name=='launch_search.py':s=s.replace('frozen-classical9-ascending','frozen-classical12-ascending')
 if name=='preflight_search.py':
  s=s.replace("assert public['officialScore']>0", "assert public['id']=='9dc3798c-93e0-4da4-a6a9-37586737c4af','Public parent changed; require a new reviewed qualification decision'\nassert public['officialScore']>0")
  s=s.replace("assert shutil.disk_usage(r).free", "bound=json.loads((ws/'classical12-final-20261020/WATCH_SOURCE.json').read_text());assert all(sha(ws/'classical12-final-20261020'/p)==h for p,h in bound.items())\nassert (ws/'classical9-retirement-20261020/TERMINAL.json').is_file()\nassert shutil.disk_usage(r).free")
 p=r/name;assert not p.exists(),p;p.write_text(s,newline='\n')
print('Prepared source12 ascending launcher; not launched')
