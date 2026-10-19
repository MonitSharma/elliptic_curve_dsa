import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'product-pair-witness-20261020';bound=json.loads((r/'WATCH_SOURCE.json').read_text());assert not (r/'WATCH_RESULT.json').exists()
while not (old/'run.exit').exists():time.sleep(15)
assert all(hashlib.sha256((r/p).read_bytes()).hexdigest()==h for p,h in bound.items())
if (old/'run.exit').read_text().strip()!='0' or not (old/'RESULT.json').exists():
 (r/'WATCH_RESULT.json').write_text(json.dumps({'status':'REFUSED_OLD_SOURCE_SCREEN_NOT_PASS','at_utc':datetime.now(timezone.utc).isoformat(),'run_started':False},indent=2)+'\n');raise SystemExit(0)
result=subprocess.run(['python3',str(r/'launch.py')],check=True)
(r/'WATCH_RESULT.json').write_text(json.dumps({'status':'PRIOR_SCREEN_FINISHED_NEW_SERIAL_SCREEN_LAUNCHED','at_utc':datetime.now(timezone.utc).isoformat(),'launch_exit':result.returncode},indent=2)+'\n')
