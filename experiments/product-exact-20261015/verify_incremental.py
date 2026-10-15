"""Validate every target artifact from immutable base+supplement without extraction."""
import hashlib,json,sys,tarfile
from pathlib import Path
base_path=Path(sys.argv[1]);delta_path=Path(sys.argv[2]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tarfile.open(base_path,'r:gz') as base,tarfile.open(delta_path,'r:gz') as delta:
    manifest=json.load(delta.extractfile('increment/manifest.json'));assert sha(base_path)==manifest['base_archive_sha256']
    old_bytes=delta.extractfile('increment/base-receipt.json').read();assert hashlib.sha256(old_bytes).hexdigest()==manifest['base_receipt_sha256'];old=json.loads(old_bytes)
    assert json.load(base.extractfile('receipt.json'))==old
    receipt_bytes=delta.extractfile('increment/current-receipt.json').read();assert hashlib.sha256(receipt_bytes).hexdigest()==manifest['current_receipt_sha256'];receipt=json.loads(receipt_bytes);stored=set(manifest['stored_new_or_changed_paths']);aliases=manifest['copy_from_base_artifact_path']
    for rel,h in receipt['files'].items():
        if rel in stored:data=delta.extractfile('increment/artifacts/'+rel).read()
        elif rel in manifest.get('exact_gzip_mtime_byte_patches',{}):
            patch=manifest['exact_gzip_mtime_byte_patches'][rel];data=base.extractfile('evidence/'+patch['base_path']).read();replacement=bytes.fromhex(patch['mtime_bytes_hex']);assert data[:3]==b'\x1f\x8b\x08' and len(replacement)==4;data=data[:4]+replacement+data[8:]
        else:data=base.extractfile('evidence/'+aliases.get(rel,rel)).read()
        assert hashlib.sha256(data).hexdigest()==h,rel
    assert len(receipt['files'])==manifest['current_artifacts']
print(json.dumps({'status':'ALL_BASE_PLUS_SUPPLEMENT_TARGET_HASHES_VERIFIED','target_artifacts':len(receipt['files']),'base_archive_sha256':sha(base_path),'supplement_sha256':sha(delta_path)}),flush=True)
