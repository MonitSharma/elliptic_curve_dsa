from pathlib import Path
import hashlib,json,tarfile,io
root=Path(__file__).resolve().parent
files={}
for p in sorted(root.iterdir()):
 if p.is_file() and p.name not in ['evidence.tar.gz','receipt.json','manifest.json','archive.log','archive.exit','archive.pid']:
  files[p.name]=p
for directory,names in [('rail-masks-20261016',['rail8_masks.c','rail8.h','librail8_masks.so','RESULT.json','DECLARATION.json']),('simd-rails-20261015',['steps.bin','denominator-pairs.bin','reference-flags.bin'])]:
 for name in names:files['frozen-inputs/'+directory+'/'+name]=root.parent/directory/name
manifest={name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for name,p in files.items()}
raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(root/'manifest.json').write_bytes(raw)
with tarfile.open(root/'evidence.tar.gz','w:gz',compresslevel=6) as tar:
 for name,p in files.items():tar.add(p,arcname=name)
 info=tarfile.TarInfo('manifest.json');info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
with tarfile.open(root/'evidence.tar.gz','r:gz') as tar:
 for name,entry in manifest.items():assert hashlib.sha256(tar.extractfile(name).read()).hexdigest()==entry['sha256']
receipt={'status':'ALL_ARTIFACT_HASHES_VERIFIED','members':len(manifest),'archive_bytes':(root/'evidence.tar.gz').stat().st_size,'archive_sha256':hashlib.sha256((root/'evidence.tar.gz').read_bytes()).hexdigest(),'source_sha256':manifest['rail8_tail64.c']['sha256'],'library_sha256':manifest['librail8_tail64.so']['sha256'],'advisory_only':True,'production_changed':False}
(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
