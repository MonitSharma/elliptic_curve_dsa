"""Snapshot immutable qualification/launch evidence; exclude live nonce rows."""
import hashlib,io,json,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;files={};omitted={}
def add(p):
    name=str(p.relative_to(ws));item={'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()}
    if p.stat().st_size<=5_000_000:files[name]=item
    else:omitted[name]=item
q=ws/'product-parent-sat-20261019/parent4-filter'
for p in q.rglob('*'):
    if not p.is_file() or 'target' in p.relative_to(q).parts:continue
    if p.suffix in {'.rs','.py','.sh','.toml','.lock','.json','.jsonl','.log','.sha256','.exit'}:add(p)
for p in r.iterdir():
    if not p.is_file():continue
    if p.suffix in {'.rs','.py','.sh','.pid'} or p.name in {'ACCEPTANCE.json','CONTROL.json','TOOL_DIFF_AUDIT.json','run-record.json','search-preflight.json','SEARCH-SOURCE.sha256','PREPARE-V1-PATH-ERROR.json','build.exit','prepare-v2.exit','order-tests.log','build.log','control.jsonl'}:add(p)
for p in (r/'tool').iterdir():
    if p.is_file() and p.suffix in {'.rs','.toml','.lock'}:add(p)
f=ws/'parent4-final-sat-20261019'
for p in f.iterdir():
    if p.is_file() and (p.suffix in {'.py','.sh','.pid'} or p.name=='WATCH_SOURCE.json'):add(p)
for p in (q/'tool/target/release/value_prefilter',r/'tool/target/release/value_prefilter'):omitted[str(p.relative_to(ws))]={'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'server_root':str(ws),'scope':'Completed qualification and frozen launch receipts; live nonce rows remain on server','included_files':files,'larger_files_preserved_on_server':omitted}
name='qualification-launch-evidence-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.tar.gz';archive=r/name
with tarfile.open(archive,'x:gz') as a:
    for p in sorted(files):a.add(ws/p,arcname=p)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
receipt={'archive':name,'bytes':archive.stat().st_size,'sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'files':len(files),'omitted':omitted}
(r/'CHECKPOINT-EVIDENCE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
