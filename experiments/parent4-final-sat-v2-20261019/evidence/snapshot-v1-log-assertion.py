"""Read-only source/path repair checkpoint; never touches watched scripts."""
import hashlib,io,json,os,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
control=json.loads((r/'PATH-CONTROL.json').read_text());assert control['status']=='FROZEN_PARENT4_FINALIZER_ALL_INPUT_PATHS_AND_HASHES_PASS'
switch=json.loads((r/'SWITCH.json').read_text());assert switch['status']=='STALE_PATH_WAITING_MANAGER_REPLACED'
pid=int((r/'watch.pid').read_text());assert pid==switch['new_pid']
assert Path(f'/proc/{pid}/cwd').resolve()==r and b'watch.py' in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
assert '6 terminal-auditor controls passed' in (r/'auditor-tests.log').read_text()
files={}
for p in r.iterdir():
    if not p.is_file() or p.name.startswith(('evidence','EVIDENCE','watch.log','watch.nohup')):continue
    files[p.name]={'bytes':p.stat().st_size,'sha256':sha(p)}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'watch_pid':pid,'scope':'Live waiting watcher, not final native benchmark. Corrected path and six corruption controls passed. Existing search/gate unchanged.','included_files':files}
with tarfile.open(r/'evidence.tar.gz','x:gz') as a:
    for p in sorted(files):a.add(r/p,arcname=p)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
p=r/'evidence.tar.gz';(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'archive':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'files':len(files)},indent=2)+'\n')
print('Corrected watcher source/path checkpoint saved; watcher untouched')
