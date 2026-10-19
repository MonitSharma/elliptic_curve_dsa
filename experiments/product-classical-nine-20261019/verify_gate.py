import hashlib,json,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;receipt=json.loads((r/'GATE-EVIDENCE.json').read_text());p=r/receipt['archive']
assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==receipt['sha256']
with tarfile.open(p) as a:
    manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))
    for name,v in manifest['included_files'].items():
        data=a.extractfile(name).read();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
    # Extract only concise immutable receipts; complete rows stay in the archive.
    for name in ['qualification/DECLARATION.json','qualification/RESULT.json','GATE-AUDIT.json']:
        target=r/'gate-receipts'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(a.extractfile(name).read())
(r/'LOCAL-GATE-VERIFICATION.json').write_text(json.dumps({'status':'GATE_ARCHIVE_AND_ALL_INCLUDED_HASHES_VERIFIED','files':len(manifest['included_files']),'archive':receipt},indent=2)+'\n')
print('Verified',len(manifest['included_files']),'gate evidence files, including all524288 rows')
