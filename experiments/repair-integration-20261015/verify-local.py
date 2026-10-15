"""Verify every archived source/log hash and the independent source patches."""
from pathlib import Path
import json,hashlib,gzip,tarfile
root=Path(__file__).resolve().parent
with tarfile.open(root/'evidence.tar.gz') as tar:
    for m in tar.getmembers():
        assert not m.issym() and not m.islnk()
        target=(root/m.name).resolve();assert target.is_relative_to(root.resolve())
    tar.extractall(root,filter='data')
e=root/'evidence';r=json.loads((e/'receipt.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
for rel,d in r['archives'].items():
    f=e/d['path'];b=f.read_bytes();assert sha(b)==d['archive_sha256'],rel
    if d['path'].endswith('.gz') and not rel.endswith('.gz'):b=gzip.decompress(b)
    assert sha(b)==d['source_sha256'] and len(b)==d['bytes'],rel
for name,d in r['repos'].items():assert sha((e/'sources'/name/'tracked.patch').read_bytes())==d['patch_sha256']
assert sha((e/'external-crates.patch').read_bytes())==r['external_crates_patch_sha256']
result={'artifacts_verified':len(r['archives']),'candidate_patches_verified':len(r['repos']),'external_crates_patch_verified':True,'score':None,'invalidated_outputs':r['invalidated_outputs']}
(root/'local-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
