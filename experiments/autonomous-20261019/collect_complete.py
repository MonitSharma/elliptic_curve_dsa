"""Snapshot completed research cycles; never treats a live log as terminal."""
import hashlib,io,json,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parent.parent
configs={
 'product-mr-order-20261019':(['run.exit'],{'CONTROL-CORE.json':'PROTECTED_SIMULATOR_EVENT_LABEL_BIJECTION_CONTROL_PASS','CONTROL-CLEAN.json':'PROTECTED_SIMULATOR_EVENT_LABEL_BIJECTION_CONTROL_PASS'}),
 'product-support-tight-20261019':(['run.exit'],{'CONTROL-ORIGINAL.json':'PROTECTED_SIMULATOR_ARBITRARY_INPUT_TRANSCRIPT_CONTROL_PASS','CONTROL-SCHEDULED.json':'PROTECTED_SIMULATOR_ARBITRARY_INPUT_TRANSCRIPT_CONTROL_PASS','CONTROL-MR.json':'PROTECTED_SIMULATOR_EVENT_LABEL_BIJECTION_CONTROL_PASS'}),
 'product-support-prune-20261019':(['run.exit','control.exit'],{'TRANSCRIPT-CONTROL.json':'PROTECTED_SIMULATOR_ARBITRARY_INPUT_TRANSCRIPT_CONTROL_PASS'}),
}
name=sys.argv[1];exits,controls=configs[name];r=root/name
for p in exits:assert (r/p).read_text().strip()=='0',p
for p,status in controls.items():assert json.loads((r/p).read_text())['status']==status,p
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files={};omitted={}
for p in r.rglob('*'):
    if not p.is_file() or 'target' in p.relative_to(r).parts or p.name.startswith(('evidence','EVIDENCE')):continue
    item={'bytes':p.stat().st_size,'sha256':sha(p)};key=str(p.relative_to(r))
    if p.suffix=='.bin' or p.stat().st_size>5_000_000:omitted[key]=item
    else:files[key]=item
manifest={'server_directory':str(r),'captured_utc':datetime.now(timezone.utc).isoformat(),'terminal_exits':{p:0 for p in exits},'passing_tool_controls':controls,'included_files':files,'larger_files_preserved_on_server':omitted}
p=r/'evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for key in sorted(files):a.add(r/key,arcname=key)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
receipt={'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files),'omitted':omitted}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'directory':name,'archive':p.name,'bytes':p.stat().st_size,'sha256':receipt['sha256'],'files':len(files),'omitted':len(omitted)}))
