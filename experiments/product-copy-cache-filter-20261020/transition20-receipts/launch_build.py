import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'build.pid').exists()
assert json.loads((r.parent/'product-copy-cache-proof-20261020/TRANSFER.json').read_text())['status']=='COPY_CACHE_VALUE_PHASE_AND_PHYSICAL_RNG_TRANSFER_AUDIT_PASS'
with (r/'build-nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run-build.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'build.pid').write_text(str(p.pid)+'\n');print(json.dumps({'build_pid':p.pid,'new_source_nonce_tests_allowed':False}))
