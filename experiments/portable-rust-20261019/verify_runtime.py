import hashlib,json,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;p=r/'runtime.tar.gz';receipt=json.loads((r/'RUNTIME.json').read_text())
assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==receipt['sha256']
dest=r/'runtime';dest.mkdir(exist_ok=False)
with tarfile.open(p) as a:
    manifest=json.load(a.extractfile('MANIFEST.json'))
    assert len(manifest['included_files'])==receipt['files']
    for key,item in manifest['included_files'].items():
        m=a.getmember(key);assert m.isfile() and not Path(key).is_absolute() and '..' not in Path(key).parts
        raw=a.extractfile(m).read();assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
        out=dest/key;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
    (r/'MEMBER-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'ARCHIVE_AND_EVERY_COMPILER_DEPENDENCY_HASH_VERIFIED','receipt':receipt},indent=2)+'\n')
print('Verified',receipt['files'],'portable compiler/dependency files')
