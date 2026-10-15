from pathlib import Path
import hashlib,io,json,tarfile
root=Path(__file__).resolve().parent
with tarfile.open(root/'evidence.tar.gz') as data:
 source=json.load(data.extractfile('wide67/native-source.json'));result=json.load(data.extractfile('wide67/RESULT.json'));raw=data.extractfile('wide67/point-add-source.tar.gz').read()
 assert hashlib.sha256(raw).hexdigest()==result['full_source_archive_sha256']
 with tarfile.open(fileobj=io.BytesIO(raw)) as inner:
  for name,sha in source.items():assert hashlib.sha256(inner.extractfile(name).read()).hexdigest()==sha,name
report={'status':'FULL_BINARY_SOURCE_LOCALLY_VERIFIED','source_files':len(source),'source_archive_sha256':hashlib.sha256(raw).hexdigest(),'frozen_stream_sha256':result['stream_sha256'],'failed_gate_retained':True}
(root/'LOCAL_SOURCE_VERIFIED.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
