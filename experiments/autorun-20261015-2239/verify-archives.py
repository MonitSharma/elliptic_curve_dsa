from pathlib import Path,PurePosixPath
import hashlib,json,tarfile,sys
for folder in sys.argv[1:]:
 root=Path(folder)
 with tarfile.open(root/'evidence.tar.gz','r:gz') as archive:
  names=archive.getnames();assert len(names)==len(set(names))
  assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
  manifest=json.load(archive.extractfile('manifest.json'))
  for name,expected in manifest.items():
   assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==expected,name
 (root/'verified-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(folder,': verified',len(manifest),'artifacts')
