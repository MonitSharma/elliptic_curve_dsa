"""Seal completed coordinator tests/build inputs, keeping live logs untouched."""
import hashlib,io,json,os,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v14.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
transition=ws/'autonomous-20261019/FINALIZER-V2-TRANSITION.json';assert json.loads(transition.read_text())['status']=='OLD_IDLE_WATCHER_RETIRED_NEW_QUEUE_FINALIZER_LIVE'
configs={
 'classical9-final-v2-20261019':'New idle queue-only coordinator is live. Six corruption and complete native/runtime/gate path controls pass. Exact bound auditor/native preparation/watch logic unchanged; only final shell root and explicit resource registry change. Old idle watcher retired intentionally with all source unchanged. No circuit, nonce order, benchmark or selected nonce changed.',
 'product-classical-twelve-filter-20261019':'Disabled source12 filter build exited0, only source hash/opcount and exact transfer bindings differ from the fully qualified source9 tool. Idle waiter is bound/live; source12 final gate remains pending, no new-source nonce tests or production changes.'}
for name,scope in configs.items():
    r=ws/name
    if name.endswith('filter-20261019'):
        assert (r/'build.exit').read_text().strip()=='0' and not (r/'QUALIFICATION-START.json').exists()
        prep=json.loads((r/'PREPARATION.json').read_text());assert all(sha(r/'tool'/p)==v['sha256'] for p,v in prep['files'].items())
        assert sha(r/'validate.py')==prep['validation_driver_sha256']
        assert sha(r/'tool/target/release/value_prefilter')==(r/'BINARY.sha256').read_text().split()[0]
    bound=json.loads((r/'WATCH_SOURCE.json').read_text());assert all(sha(r/p)==h for p,h in bound.items())
    files={};data={}
    for p in r.rglob('*'):
        rel=p.relative_to(r)
        if not p.is_file() or any(x in rel.parts for x in ['target','candidate','__pycache__','evidence','cycle-receipts']):continue
        if p.name in ['watch.log','watch-nohup.log'] or p.name.startswith(('v14-cycle','V14-CYCLE','LOCAL-VERIFICATION')):continue
        assert p.stat().st_size<1_000_000
        raw=p.read_bytes();key=rel.as_posix();files[key]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};data[key]=raw
    extras={'resource-profile.json':(json.dumps(profile,indent=2)+'\n').encode(),'FINALIZER-V2-TRANSITION.json':transition.read_bytes()}
    for key,raw in extras.items():files[key]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};data[key]=raw
    manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'server_directory':str(r),'scope':scope,'included_files':files}
    p=r/'v14-cycle.tar.gz'
    with tarfile.open(p,'x:gz') as a:
        for key,raw in sorted(data.items()):m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
        raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
    receipt={'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files),'scope':scope}
    (r/'V14-CYCLE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'directory':name,**receipt}))
