from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent;receipt=json.loads((root/'receipt.json').read_text());archive=root/'evidence.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==receipt['archive_sha256']
with tarfile.open(archive,'r:gz') as tar:
 manifest=json.load(tar.extractfile('manifest.json'));assert len(manifest)==receipt['members']
 for name,entry in manifest.items():
  data=tar.extractfile(name).read();assert len(data)==entry['bytes'];assert hashlib.sha256(data).hexdigest()==entry['sha256'],name
result={'status':'LOCAL_ALL_ARCHIVE_MEMBERS_VERIFIED','members':len(manifest),'archive_sha256':receipt['archive_sha256']}
(root/'LOCAL_VERIFIED.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
