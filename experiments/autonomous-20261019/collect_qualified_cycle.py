"""Read-only checkpoint of terminal qualification and immutable live-job inputs."""
import hashlib,io,json,tarfile
from datetime import datetime,timezone
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
filter9=ws/'product-classical-nine-filter-20261019'
op=ws/'product-classical-nine-operational-20261019'
final=ws/'classical9-final-20261019'
retired=ws/'parent4-retirement-20261019'
assert (filter9/'qualification.exit').read_text().strip()=='0'
assert json.loads((filter9/'RESULT.json').read_text())['status']=='DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS'
assert (op/'control.exit').read_text().strip()=='0'
assert json.loads((op/'CONTROL.json').read_text())['status']=='CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX'
assert json.loads((retired/'TERMINAL.json').read_text())['status']=='OLD_SOURCE_STOPPED_CLEANLY_NO_PASS_ALL_LOGS_PRESERVED'
assert 'UNBOUND_NOT_ACCEPTED' not in (final/'audit-terminal.py').read_text()
configs={
 filter9: 'Completed disabled-runtime qualification, including every diagnostic row and all failed build admissions. Binary stays server-side; no production nonce selected.',
 op: 'Accepted operational source, build, control and immutable production-launch inputs. Live worker rows/logs are deliberately excluded; no complete coverage or record claimed.',
 final: 'Actual runtime-bound immutable finalizer source and passed path/corruption controls. Watcher is live; no selected nonce or official benchmark yet.',
 retired: 'Old source clean terminal receipt and exact hashes of all preserved logs. Counts are controller-reported; no full old JSONL coverage audit or nonce selection claimed.',
}
for r,scope in configs.items():
    files={};omitted={};data={}
    for p in r.rglob('*'):
        rel=p.relative_to(r);key=rel.as_posix()
        if not p.is_file() or p.is_symlink() or any(x in rel.parts for x in ['target','candidate','.git','__pycache__','evidence','cycle-receipts']):continue
        if p.name.startswith(('evidence','EVIDENCE','LOCAL-','qualified-cycle','QUALIFIED-CYCLE')):continue
        if r==op and (p.name.startswith('worker') or p.name in ['search.log','search-nohup.log','submissions.json']):continue
        if r==final and p.name in ['watch.log','watch-nohup.log']:continue
        before=p.stat();raw=p.read_bytes();after=p.stat()
        assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),str(p)
        item={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        if p.suffix in ['.bin','.so','.o','.a'] or len(raw)>5_000_000:omitted[key]=item
        else:files[key]=item;data[key]=raw
    if r==retired:
        for name,path in [('old-search-RESULT.json',ws/'parent4-operational-sat-20261019/RESULT.json'),('old-final-WATCH_RESULT.json',ws/'parent4-final-sat-v2-20261019/WATCH_RESULT.json')]:
            raw=path.read_bytes();files[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};data[name]=raw
    manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'server_directory':str(r),'scope':scope,'included_files':files,'large_files_preserved_on_server':omitted}
    archive=r/'qualified-cycle.tar.gz'
    with tarfile.open(archive,'x:gz') as a:
        for key,raw in sorted(data.items()):
            m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
        raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
    receipt={'archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(files),'scope':scope}
    (r/'QUALIFIED-CYCLE.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'directory':r.name,**receipt}),flush=True)
