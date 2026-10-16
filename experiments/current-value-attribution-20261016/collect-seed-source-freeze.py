from pathlib import Path
import json,hashlib,tarfile,shutil
b=Path('/home/hclau/ecdsa_research');r=b/'seed-restore-20261016';e=b/'current-value-attribution-20261016';n='native-source-freeze-v1';d=r/n;assert not d.exists();d.mkdir();assert(r/'native-verification.exit').read_text().strip()=='0'
for p in r.iterdir():
 if p.is_file()and p.suffix in['.json','.log','.exit','.patch','.rs','.bin']and not p.name.startswith('preserved-')and p.stat().st_size<25_000_000:shutil.copy2(p,d/p.name)
for folder in ['candidate/src/point_add','tool/src']:
 for p in(r/folder).rglob('*'):
  if p.is_file():q=d/p.relative_to(r);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for folder in['candidate','tool']:
 for name in['Cargo.toml','Cargo.lock','rust-toolchain.toml']:
  p=r/folder/name
  if p.exists():q=d/p.relative_to(r);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in['prepare-seed-candidate.py','prepare-seed-protected.py','run-seed-native.sh','verify-seed-native.py','run-seed-fresh.sh','wait-seed-native-then-fresh.sh']:
 q=d/'scripts'/name;q.parent.mkdir(exist_ok=True);shutil.copy2(e/name,q)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin=dict(status='FROZEN NATIVE SOURCE/PROOFS; SOLE FRESH CENSUS ACTIVE, NO OUTCOME CLAIM',diagnosis_archive_sha256=sha(e/'seed-diagnosis-v1.tar.gz'),native=json.loads((r/'native-verification.json').read_text()),external_streams={str(p):dict(bytes=p.stat().st_size,sha256=sha(p),status='server-only, not archive member')for p in[r/'candidate/ops.bin',b/'product-exact-20261015/tip/ops.bin']})
(d/'SOURCE-PIN.json').write_text(json.dumps(pin,indent=2)+'\n');files={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()};(d/'MANIFEST.json').write_text(json.dumps(dict(files=files,external=pin['external_streams'],diagnosis_archive_sha256=pin['diagnosis_archive_sha256']),indent=2)+'\n')
p=r/(n+'.tar.gz')
with tarfile.open(p,'w:gz')as tf:tf.add(d,arcname=n)
with tarfile.open(p)as tf:
 for f,v in files.items():x=tf.extractfile(n+'/'+f).read();assert len(x)==v['bytes']and hashlib.sha256(x).hexdigest()==v['sha256']
out=dict(status='PASS',archive=str(p),sha256=sha(p),bytes=p.stat().st_size,verified_members=len(files));(r/(n+'-receipt.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
