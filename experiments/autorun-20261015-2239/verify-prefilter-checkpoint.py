from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
root=Path(__file__).resolve().parent.parent/'prefilter-20261015';archive=root/'evidence-local.tar.gz'
sha=hashlib.sha256(archive.read_bytes()).hexdigest();assert sha==(root/'evidence-local.tar.gz.sha256').read_text().split()[0]
with tarfile.open(archive) as data:
 names=data.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 manifest=json.load(data.extractfile('evidence/local-archive-manifest.json'))
 for name,record in manifest['files'].items():
  payload=data.extractfile(name).read();assert len(payload)==record['bytes'];assert hashlib.sha256(payload).hexdigest()==record['sha256'],name
report={'archive_sha256':sha,'files_verified':len(manifest['files']),'no_extraction_or_active_file_changes':True}
(root/'root-checkpoint-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
