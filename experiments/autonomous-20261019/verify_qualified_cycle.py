"""Verify all checkpoint members and materialize concise review receipts."""
import hashlib,json,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
names=['product-classical-nine-filter-20261019','product-classical-nine-operational-20261019','classical9-final-20261019','parent4-retirement-20261019']
for name in names:
    r=ws/name;receipt=json.loads((r/'QUALIFIED-CYCLE.json').read_text());p=r/receipt['archive']
    assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==receipt['sha256']
    with tarfile.open(p) as a:
        manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))
        for key,item in manifest['included_files'].items():
            raw=a.extractfile(key).read();assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
            if '/' not in key and (key.endswith('.json') or key.endswith('.pid') or key.endswith('.exit')):
                out=r/'cycle-receipts'/key;out.parent.mkdir(exist_ok=True);out.write_bytes(raw)
            if name=='classical9-final-20261019' and key in ['audit-terminal.py','run-final.sh']:
                (r/key).write_bytes(raw)  # download actual bound source; never upload a stale recipe
    (r/'LOCAL-QUALIFIED-VERIFICATION.json').write_text(json.dumps({'status':'ARCHIVE_AND_ALL_INCLUDED_HASHES_VERIFIED','receipt':receipt},indent=2)+'\n')
    print(name,receipt['files'],'verified')
