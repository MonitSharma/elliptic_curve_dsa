from pathlib import Path,PurePosixPath
import hashlib,io,json,tarfile
base=Path(__file__).resolve().parent.parent
root=base/'product67-native-20261016'
with tarfile.open(root/'evidence.tar.gz') as outer:
 source=json.load(outer.extractfile('product67/native-source.json'))
 raw=outer.extractfile('product67/point-add-source.tar.gz').read();result=json.load(outer.extractfile('product67/RESULT.json'))
 assert hashlib.sha256(raw).hexdigest()==result['full_source_archive_sha256']
 with tarfile.open(fileobj=io.BytesIO(raw)) as inner:
  for name,sha in source.items():assert hashlib.sha256(inner.extractfile(name).read()).hexdigest()==sha,name
 (root/'ROOT_SOURCE_VERIFIED.json').write_text(json.dumps({'source_files':len(source),'inner_full_binary_source_sha256':hashlib.sha256(raw).hexdigest(),'all_source_hashes_match':True},indent=2)+'\n')
root=base/'product25-operational-20261016';receipt=json.loads((root/'checkpoint-receipt.json').read_text());raw=(root/'checkpoint-evidence.tar.gz').read_bytes();assert hashlib.sha256(raw).hexdigest()==receipt['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(raw)) as data:
 names=data.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 path=[n for n in names if n.endswith('/CHECKPOINT.json')];assert len(path)==1
 manifest=json.load(data.extractfile(path[0]));prefix=path[0][:-len('CHECKPOINT.json')]
 for name,r in manifest['source_and_snapshot_files'].items():
  payload=data.extractfile(prefix+name).read();assert len(payload)==r['bytes'] and hashlib.sha256(payload).hexdigest()==r['sha256'],name
 (root/'ROOT_CHECKPOINT_VERIFIED.json').write_text(json.dumps({'archive_sha256':receipt['archive_sha256'],'snapshot_files_verified':len(manifest['source_and_snapshot_files']),'live_checkpoint_not_terminal_result':True},indent=2)+'\n')
print('Verified complete product67 source and immutable operational search snapshot')
