from pathlib import Path
import hashlib,json,tarfile,subprocess,shutil
p=Path('/home/hclau/ecdsa_research/simd-prefilter-20261015')
snap=p/'dependency-snapshot';snap.mkdir(exist_ok=True)
s=Path('/home/hclau/ecdsa_research/shake8-20261015')
for name in ['shake8.c','shake8.h','libshake8.so','vendor-revision.txt','STATUS.md','manifest.json','validation.log']:
 if (s/name).exists():shutil.copy2(s/name,snap/name)
baseline=Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline')
files=[baseline/'Cargo.toml',baseline/'Cargo.lock',baseline/'src/sim.rs',baseline/'src/circuit.rs',baseline/'src/weierstrass_elliptic_curve.rs']
manifest={'protected_dependency':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in files if x.exists()},'git_status':subprocess.run(['git','status','--porcelain'],cwd=baseline,capture_output=True,text=True).stdout,'files':{}}
for x in sorted(p.rglob('*')):
 if x.is_file() and 'target' not in x.parts and x.name not in ['manifest.json','evidence.tar.gz','evidence.sha256']:
  manifest['files'][str(x.relative_to(p))]={'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()}
(p/'manifest.json').write_text(json.dumps(manifest,indent=2))
with tarfile.open(p/'evidence.tar.gz','w:gz') as t:
 for x in sorted(p.rglob('*')):
  if x.is_file() and 'target' not in x.parts and x.name not in ['evidence.tar.gz','evidence.sha256']:t.add(x,arcname=str(x.relative_to(p)))
(p/'evidence.sha256').write_text(hashlib.sha256((p/'evidence.tar.gz').read_bytes()).hexdigest()+'  evidence.tar.gz\n')
print((p/'evidence.sha256').read_text())
