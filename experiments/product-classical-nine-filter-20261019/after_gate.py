"""Wait for the existing one-shot gate; never declares/repeats it or searches."""
import datetime,hashlib,json,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;n=r.parent/'product-classical-nine-20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bound={p.name:sha(p) for p in r.iterdir() if p.suffix in ['.py','.sh']}
(r/'WATCH_SOURCE.json').write_text(json.dumps(bound,indent=2)+'\n')
while not (n/'gate-v2.exit').exists() or not (r/'build.exit').exists():time.sleep(20)
assert all(sha(r/p)==h for p,h in bound.items())
gate=json.loads((n/'qualification/RESULT.json').read_text()) if (n/'qualification/RESULT.json').exists() else None
if (n/'gate-v2.exit').read_text().strip()!='0' or (r/'build.exit').read_text().strip()!='0' or not gate or gate['status']!='FAILURE_GATE_PASS':
    (r/'WATCH_RESULT.json').write_text(json.dumps({'status':'NO_RUNTIME_QUALIFICATION_GATE_OR_BUILD_DID_NOT_PASS','gate_status':gate and gate['status'],'no_gate_rerun_or_nonce_search':True},indent=2)+'\n');raise SystemExit(0)
with (r/'qualification-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-qualify.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'qualification.pid').write_text(str(p.pid)+'\n');code=p.wait()
(r/'WATCH_RESULT.json').write_text(json.dumps({'status':'DISABLED_RUNTIME_QUALIFICATION_FINISHED' if code==0 else 'DISABLED_RUNTIME_QUALIFICATION_FAILED','exit_code':code,'authoritative_rejection_enabled':False,'nonce_selected':None},indent=2)+'\n')
