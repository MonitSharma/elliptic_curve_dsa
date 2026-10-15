from pathlib import Path,PurePosixPath
import hashlib,io,json,tarfile
root=Path(__file__).resolve().parent;path=root/'evidence.tar.gz';counts={}
with tarfile.open(path) as outer:
 for name in ['product53','wide43']:
  result=json.load(outer.extractfile(name+'/RESULT.json'));sources=json.load(outer.extractfile(name+'/native-source.json'))
  data=outer.extractfile(name+'/point-add-source.tar.gz').read();assert hashlib.sha256(data).hexdigest()==result['full_point_add_source_archive_sha256']
  with tarfile.open(fileobj=io.BytesIO(data)) as inner:
   names=inner.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
   for rel,h in sources.items():assert hashlib.sha256(inner.extractfile(rel).read()).hexdigest()==h,rel
   assert len([m for m in inner if m.isfile()])==len(sources)
  counts[name]=len(sources)
receipt={'outer_archive_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'full_submission_source_files_verified':counts,'all_inner_and_outer_source_hashes_match':True}
(root/'LOCAL_ARCHIVE_VERIFIED.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
