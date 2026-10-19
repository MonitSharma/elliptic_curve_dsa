import hashlib,json,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;receipt=json.loads((r/'BUILD-EVIDENCE.json').read_text());p=r/receipt['archive']
assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt['sha256']
with tarfile.open(p) as a:
    manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))
    for name,v in manifest['included_files'].items():
        data=a.extractfile(name).read();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
(r/'LOCAL-BUILD-VERIFICATION.json').write_text(json.dumps({'status':'BUILD_ARCHIVE_AND_ALL_INCLUDED_HASHES_VERIFIED','files':len(manifest['included_files']),'archive':receipt},indent=2)+'\n')
print('Verified',len(manifest['included_files']),'build/source files')
