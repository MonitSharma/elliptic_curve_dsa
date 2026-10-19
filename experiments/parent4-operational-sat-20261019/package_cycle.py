"""Verify peak archive and record large local evidence without deleting it."""
import hashlib,json,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];e=root/'experiments'
peak=e/'product-peak-synthesis-20261019';receipt=json.loads((peak/'EVIDENCE-MANIFEST.json').read_text())
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert sha(peak/receipt['archive'])==receipt['sha256']
with tarfile.open(peak/receipt['archive']) as a:
    manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))
    for name,item in manifest['included_files'].items():
        raw=a.extractfile(name).read();assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
    dest=peak/'evidence';dest.mkdir(exist_ok=False)
    for member in a.getmembers():
        assert member.isfile() and Path(member.name).name==member.name
        (dest/member.name).write_bytes(a.extractfile(member).read())
(peak/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'ALL_PEAK_ARCHIVE_HASHES_VERIFIED','archive':receipt,'files':len(manifest['included_files'])},indent=2)+'\n')
directories=['product-parent-sat-20261019','parent4-operational-sat-20261019','parent4-final-sat-20261019','product-anf-20261019','product-peak-synthesis-20261019','product-schedule-20261019']
large={}
for name in directories:
    for p in (e/name).rglob('*'):
        if p.is_file() and p.stat().st_size>5_000_000:
            large[str(p.relative_to(root)).replace('\\','/')]={'bytes':p.stat().st_size,'sha256':sha(p),'preserved_locally':True}
(e/'LARGE-FILES-MANIFEST-20261019-autonomous.json').write_text(json.dumps({'scope':'New autonomous proof/peak/schedule/search checkpoints only; large files retained and excluded from Git','files':large},indent=2)+'\n')
print('Peak files verified:',len(manifest['included_files']),'large local files:',len(large))
