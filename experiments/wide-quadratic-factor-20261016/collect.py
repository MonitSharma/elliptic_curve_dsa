from pathlib import Path
import hashlib,json,tarfile,io
root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (root/'run.exit').read_text().strip()==(root/'controls.exit').read_text().strip()=='0'
files=[p for p in root.rglob('*') if p.is_file() and p.name not in ['evidence.tar.gz','manifest.json','receipt.json','collect.log']]
manifest={'files':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size}for p in files},'hashrefs':[]}
for name in ['evidence.tar.gz','evidence/final-ops.bin']:
 p=root.parent/'wide15-record-20261016'/name;manifest['hashrefs'].append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(root/'manifest.json').write_bytes(raw)
with tarfile.open(root/'evidence.tar.gz','w:gz') as t:
 for p in files:t.add(p,arcname=str(p.relative_to(root)),recursive=False)
 info=tarfile.TarInfo('manifest.json');info.size=len(raw);t.addfile(info,io.BytesIO(raw))
with tarfile.open(root/'evidence.tar.gz','r:gz') as t:
 for name,item in manifest['files'].items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==item['sha256']
receipt={'status':'ALL_NEW_ARTIFACTS_AND_EXISTING_INPUT_HASHREFS_VERIFIED','members':len(files),'hashrefs':manifest['hashrefs'],'archive_bytes':(root/'evidence.tar.gz').stat().st_size,'archive_sha256':sha(root/'evidence.tar.gz')}
(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
