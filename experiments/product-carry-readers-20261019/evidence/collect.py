"""Archive completed source-only evidence; large tapes stay source-hashed on server."""
import hashlib,io,json,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent
for name in ['run.exit','profile.exit','gaps.exit']:assert (r/name).read_text().strip()=='0',name
assert json.loads((r/'profile-control.json').read_text())['status']=='INSTRUMENTATION_OUTPUT_AND_ALL_EXISTING_FIELDS_IDENTICAL'
coverage=json.loads((r/'coverage.json').read_text())
assert not coverage['all_structural_cells']['complete_cover']
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files={};omitted={}
for p in r.rglob('*'):
    if not p.is_file() or 'target' in p.relative_to(r).parts or p.name.startswith(('evidence','EVIDENCE')):continue
    key=p.relative_to(r).as_posix();item={'bytes':p.stat().st_size,'sha256':sha(p)}
    if p.suffix=='.bin' or p.stat().st_size>5_000_000:omitted[key]=item
    else:files[key]=item
manifest={'server_directory':str(r),'captured_utc':datetime.now(timezone.utc).isoformat(),
          'terminal_exits':{'run.exit':0,'profile.exit':0,'gaps.exit':0},
          'included_files':files,'larger_files_preserved_on_server':omitted}
p=r/'evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for key in sorted(files):a.add(r/key,arcname=key)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
receipt={'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files),'omitted':omitted}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='omitted'}))
