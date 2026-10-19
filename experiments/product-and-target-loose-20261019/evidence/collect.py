"""Archive completed source-only evidence; large tapes stay source-hashed on server."""
import hashlib,io,json,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent
for name in ['run-v2.exit']:assert (r/name).read_text().strip()=='0',name
assert (r/'run.exit').read_text().strip()=='101'
assert json.loads((r/'control.json').read_text())['status']=='PROTECTED_SIMULATOR_EVENT_SUBSEQUENCE_CONTROL_PASS'
assert json.loads((r/'COMPARE-STRICT.json').read_text())['status']=='GENERALIZED_SCREEN_ADMITS_NO_NEW_SITE_AND_EXACT_SAME_COMPLETE_OUTPUT'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files={};omitted={}
for p in r.rglob('*'):
    if not p.is_file() or 'target' in p.relative_to(r).parts or p.name.startswith(('evidence','EVIDENCE')):continue
    key=p.relative_to(r).as_posix();item={'bytes':p.stat().st_size,'sha256':sha(p)}
    if p.suffix=='.bin' or p.stat().st_size>5_000_000:omitted[key]=item
    else:files[key]=item
manifest={'server_directory':str(r),'captured_utc':datetime.now(timezone.utc).isoformat(),
          'terminal_exits':{'run.exit':101,'run-v2.exit':0},
          'included_files':files,'larger_files_preserved_on_server':omitted}
p=r/'evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for key in sorted(files):a.add(r/key,arcname=key)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
receipt={'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files),'omitted':omitted}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='omitted'}))
