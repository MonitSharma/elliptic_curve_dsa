import hashlib,io,json,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;name=sys.argv[1]
assert name in ['classical9-final-20261019','product-classical-nine-operational-20261019']
r=ws/name;assert not (r/'watch.pid').exists() and not (r/'prepare.pid').exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
if name=='classical9-final-20261019':
    assert json.loads((r/'NATIVE-INPUT-CONTROL.json').read_text())['status']=='NATIVE_INPUTS_VERIFIED_OTHER_GATES_PENDING'
    tests=(r/'auditor-tests.log').read_text();assert 'Ran 6 tests' in tests and tests.rstrip().endswith('OK')
    assert (r/'audit-terminal.py').read_text().count('UNBOUND_NOT_ACCEPTED')==2
files={}
for p in r.rglob('*'):
    rel=p.relative_to(r)
    if not p.is_file() or any(x in rel.parts for x in ['__pycache__','target','tool','evidence']):continue
    if p.name.startswith(('evidence','EVIDENCE')):continue
    assert p.stat().st_size<1_000_000
    files[rel.as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'included_files':files,
 'scope':'Prepared code only. No operational port/build/control, runtime bind, final watcher, nonce or benchmark executed. Native-only path and6 corruption controls are preserved if present; complete gate/runtime readiness remains unproven.'}
p=r/'evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for name in sorted(files):a.add(r/name,arcname=name)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files)},indent=2)+'\n')
print(json.dumps({'directory':str(r),'files':len(files),'archive_sha256':sha(p)}))
