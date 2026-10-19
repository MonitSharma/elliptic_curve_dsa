import hashlib,io,json,tarfile
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent
assert (r/'run-v3.exit').read_text().strip()=='0'
assert (r/'trace-v2.exit').read_text().strip()=='0'
assert json.loads((r/'TRACE-CONTROL.json').read_text())['status']=='PROTECTED_SIMULATOR_ARBITRARY_INPUT_TRANSCRIPT_CONTROL_PASS'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
included={};omitted={}
for p in r.rglob('*'):
    if not p.is_file() or 'target' in p.relative_to(r).parts or p.name.startswith(('evidence','EVIDENCE')):continue
    name=str(p.relative_to(r));item={'bytes':p.stat().st_size,'sha256':sha(p)}
    if p.suffix=='.bin' or p.stat().st_size>5_000_000:omitted[name]=item
    else:included[name]=item
manifest={'server_directory':str(r),'captured_utc':datetime.now(timezone.utc).isoformat(),'included_files':included,'larger_files_preserved_on_server':omitted}
p=r/'evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for name in sorted(included):a.add(r/name,arcname=name)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
receipt={'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(included),'omitted':omitted}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
