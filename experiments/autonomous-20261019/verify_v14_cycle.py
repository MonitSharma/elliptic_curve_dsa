import hashlib,json,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
for name in ['classical9-final-v2-20261019','product-classical-twelve-filter-20261019']:
    r=ws/name;receipt=json.loads((r/'V14-CYCLE.json').read_text());p=r/receipt['archive'];assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==receipt['sha256']
    with tarfile.open(p) as a:
        manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))
        for key,item in manifest['included_files'].items():
            raw=a.extractfile(key).read();assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
            if '/' not in key and (key.endswith(('.json','.pid','.exit')) or key=='BINARY.sha256'):
                out=r/'cycle-receipts'/key;out.parent.mkdir(exist_ok=True);out.write_bytes(raw)
            if '/' not in key and key.endswith(('.py','.sh')) and (name.startswith('classical9-final') or key=='validate.py'):
                (r/key).write_bytes(raw)
    (r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'ARCHIVE_AND_ALL_INCLUDED_HASHES_VERIFIED','receipt':receipt},indent=2)+'\n');print(name,receipt['files'],'files verified')
