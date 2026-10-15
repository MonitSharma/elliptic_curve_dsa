"""Verify cache archives and add portable patches for the new research crates."""
from pathlib import Path
import tarfile,hashlib,json,difflib,gzip
top=Path(__file__).resolve().parent.parent
for name in ['cache-retention-20261015','cache-polarity-20261015','cache-idle-20261015']:
    root=top/name
    with tarfile.open(root/'evidence.tar.gz') as tar:tar.extractall(root,filter='data')
    receipt=json.loads((root/'evidence/receipt.json').read_text())
    for a in receipt['archives'].values():
        assert hashlib.sha256((root/'evidence'/a['path']).read_bytes()).hexdigest()==a['archive_sha256']
    patch=[]
    for name,a in sorted(receipt['archives'].items()):
        if name.startswith(('analyzer/','replay/')):
            b=(root/'evidence'/a['path']).read_bytes()
            if a['path'].endswith('.gz'):b=gzip.decompress(b)
            assert hashlib.sha256(b).hexdigest()==a['source_sha256']
            patch.extend(difflib.unified_diff([],b.decode().splitlines(True),fromfile='/dev/null',tofile='b/'+name))
    p=root/'research-crates.patch';p.write_text(''.join(patch),encoding='utf-8',newline='\n')
    (root/'local-verification.json').write_text(json.dumps({'archive_sha256':hashlib.sha256((root/'evidence.tar.gz').read_bytes()).hexdigest(),'verified_artifacts':len(receipt['archives']),'new_external_crates_patch_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'patch_base':'empty external research directory; submission sources are not modified','score':None},indent=2)+'\n')
    print(root.name,len(receipt['archives']))
