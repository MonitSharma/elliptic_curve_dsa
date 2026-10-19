import hashlib,json,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;receipt=json.loads((r/'EVIDENCE-MANIFEST.json').read_text());p=r/receipt['archive']
assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==receipt['sha256']
with tarfile.open(p) as a:
    manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))
    for name,item in manifest['included_files'].items():
        raw=a.extractfile(name).read();assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],name
    dest=r/'evidence';dest.mkdir(exist_ok=False)
    for member in a.getmembers():
        assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        p=dest/member.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(a.extractfile(member).read())
(r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'ARCHIVE_AND_ALL_INCLUDED_HASHES_VERIFIED','files':len(manifest['included_files']),'archive':receipt},indent=2)+'\n')
print('Verified',len(manifest['included_files']),'files')
