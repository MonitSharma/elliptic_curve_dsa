"""Source-bound snapshots of finished guard experiments, including failures."""
import hashlib,io,json,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parent.parent
configs={
 'product-guard-schedule-20261019':({'run.exit':0,'control.exit':0},{'CONTROL.json':'PROTECTED_SIMULATOR_MATERIALIZED_GUARD_PHYSICAL_TRANSCRIPT_CONTROL_PASS'}),
 'product-guard-mrfree-20261019':({'run.exit':101,'run-v2.exit':0},{'ANNOTATION-CONTROL.json':'STRONG_ANNOTATION_OUTPUT_AND_ALL_EXISTING_FIELDS_IDENTICAL','CONTROL-prior.json':'PROTECTED_SIMULATOR_MATERIALIZED_GUARD_MAPPED_EVENT_TRANSCRIPT_CONTROL_PASS','CONTROL-strong.json':'PROTECTED_SIMULATOR_MATERIALIZED_GUARD_MAPPED_EVENT_TRANSCRIPT_CONTROL_PASS'}),
 'product-two-target-20261019':({'run.exit':0},{'SIX-CASE-CONTROL.json':'ALL_SIX_FIXED_SOURCE_QUERIES_ZERO_WITH_MATCHED_SOURCE_HASHES'}),
 'product-branch-alias-20261019':({'run.exit':0},{'QUALIFICATION.json':'ALIAS_PROBE_OUTPUT_AND_ALL_EXISTING_FIELDS_IDENTICAL'}),
}
name=sys.argv[1];exits,controls=configs[name];r=root/name
for p,code in exits.items():assert int((r/p).read_text())==code,p
for p,status in controls.items():assert json.loads((r/p).read_text())['status']==status,p
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files={};omitted={}
for p in r.rglob('*'):
    if not p.is_file() or 'target' in p.relative_to(r).parts or p.name.startswith(('evidence','EVIDENCE')):continue
    key=p.relative_to(r).as_posix();item={'bytes':p.stat().st_size,'sha256':sha(p)}
    if p.suffix=='.bin' or p.stat().st_size>5_000_000:omitted[key]=item
    else:files[key]=item
manifest={'server_directory':str(r),'captured_utc':datetime.now(timezone.utc).isoformat(),
          'terminal_exits':exits,'passing_controls':controls,'included_files':files,
          'larger_files_preserved_on_server':omitted}
p=r/'evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for key in sorted(files):a.add(r/key,arcname=key)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
receipt={'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files),'omitted':omitted}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='omitted'}))
