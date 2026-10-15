from pathlib import Path
import hashlib, json, tarfile, io
r=Path(__file__).resolve().parent
out=r/'evidence-a29-conditional-transfer.tar.gz'
assert not out.exists()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
files=set()
for folder in ['a29-conditional-coverage-v1','a29-conditional-subset-v1','a29-conditional-certificate-v1']:
 for p in (r/folder).rglob('*'):
  if p.is_file():files.add(p)
for name in ['freeze-a29-conditional-transfer.py','archive-a29-conditional-transfer-evidence.py',
 'tool/src/bin/a29_retained_subset.rs','tool/src/a29_retained_subset_body.rs','tool/Cargo.toml',
 'a29-conditional-prefix-v1/ROOT_INDEPENDENT_REVIEW.json']:
 files.add(r/name)
cache=r.parent/'product-exact-20261015/repair67-universal-20261016'
for name in ['CACHE_EQUIVALENCE_CERTIFICATE.json','PER_INPUT_MASK_TRANSFER.json']:
 p=cache/name;dest=r/'a29-conditional-certificate-v1'/('CACHE67_'+name)
 assert not dest.exists();dest.write_bytes(p.read_bytes());files.add(dest)
p=r.parent/'product-exact-20261015/REPAIR67_ABI.json'
dest=r/'a29-conditional-certificate-v1/REPAIR67_ABI.json';assert not dest.exists();dest.write_bytes(p.read_bytes());files.add(dest)
refs=[]
for name,expected in [
 ('evidence-a29-paired-family-components.tar.gz','28848e9697a739fee2ca8d0b4bab1f32e0e17bb20f3f64d08cbec34bc8822dab'),
 ('evidence-a29-conditional-prefix-supplement.tar.gz','df9215093c8e24070fc07b729467ac77d86d5b6499c89e3e3d299765ce78e1ea')]:
 assert sha(r/name)==expected;refs.append(dict(path=name,sha256=expected))
cert=json.loads((r/'a29-conditional-certificate-v1/CONDITIONAL_TRANSFER_CERTIFICATE.json').read_text())
refs.extend([dict(path='product-exact-20261015/tip/ops.bin',sha256=cert['original_stream_sha256']),
 dict(path='product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin',sha256=cert['A29_stream_sha256']),
 dict(path='prefilter-20261015/evidence/mr-mask-tip-v3.bin',sha256=cert['original_mask_sha256']),
 cert['public_discrepancy_guard']])
manifest=dict(status='IMMUTABLE_CONDITIONAL_TRANSFER_AND_FIXED445_COVERAGE_NO_RUNTIME_AUTHORITY',
 files=[dict(path=p.relative_to(r).as_posix(),sha256=sha(p),size=p.stat().st_size)for p in sorted(files)],
 server_only_or_prior_archive_hashrefs=refs)
with tarfile.open(out,'w:gz')as tf:
 for p in sorted(files):tf.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();t=tarfile.TarInfo('MANIFEST.json');t.size=len(b);tf.addfile(t,io.BytesIO(b))
with tarfile.open(out)as tf:
 for row in manifest['files']:assert hashlib.sha256(tf.extractfile(row['path']).read()).hexdigest()==row['sha256']
receipt=dict(status='ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY',archive=out.name,sha256=sha(out),files=len(files),hashrefs=len(refs))
(r/'evidence/a29-conditional-transfer-archive-receipt.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps(receipt))
