"""Immutable source/failed-admission checkpoint of the live build/watcher."""
import hashlib,io,json,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
bound=json.loads((r/'WATCH_SOURCE.json').read_text());assert all(sha(r/p)==h for p,h in bound.items())
assert json.loads((r/'ADMISSION-REPAIR.json').read_text())['nonce_shots_executed']==0
files={}
for p in r.rglob('*'):
    rel=p.relative_to(r)
    if not p.is_file() or any(x in rel.parts for x in ['tool','target','__pycache__','evidence']):continue
    if p.name.startswith(('evidence','EVIDENCE')) or p.name in ['build.log','build-nohup.log','watch-nohup.log','qualification-nohup.log']:continue
    files[rel.as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Live build/disabled-qualification waiter; no current-source nonce tests before gate pass. Frozen scripts unchanged. Failed initial admission preserved. Runtime tool sources have separate PREPARATION hashes and remain on server.','included_files':files}
with tarfile.open(r/'evidence.tar.gz','x:gz') as a:
    for name in sorted(files):a.add(r/name,arcname=name)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
p=r/'evidence.tar.gz';(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files)},indent=2)+'\n')
print('Verified waiting-source bindings and saved immutable source/admission checkpoint')
