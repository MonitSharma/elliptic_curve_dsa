"""Verify every frozen receipt member without extracting untrusted archive paths."""
import hashlib,json,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;archive=r/'evidence.tar.gz';receipt=json.loads((r/'receipt.json').read_text())
assert not receipt['protected_dependency_mismatches']
assert all(not x['protected_mismatches'] for x in receipt['all_candidates'].values())
with tarfile.open(archive,'r:gz') as t:
    assert json.load(t.extractfile('receipt.json'))==receipt
    for name,h in receipt['files'].items():assert hashlib.sha256(t.extractfile('evidence/'+name).read()).hexdigest()==h,name
out={'status':'ALL_RECEIPT_FILE_HASHES_VERIFIED','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(receipt['files']),'archive_bytes':archive.stat().st_size,'protected_candidates_checked':len(receipt['all_candidates']),'protected_mismatches':[],'snapshot_directory':receipt['snapshot_directory']}
(r/'verified-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
