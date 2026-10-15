from pathlib import Path
import hashlib,json,tarfile,shutil
p=Path('/home/hclau/ecdsa_research/simd-rails-20261015');ref=Path('/home/hclau/ecdsa_research/prefilter-20261015')
snap=p/'model-snapshot';snap.mkdir(exist_ok=True)
for name in ['steps.txt','anchors.txt']:shutil.copy2(ref/'model-source'/name,snap/name)
external=[ref/'tool/src/rail_advisory.rs',ref/'evidence/census-coordinates4096.tsv',ref/'evidence/rail-advisory-population.jsonl']
manifest={'external':{},'files':{}}
for x in external:
 if x.exists():manifest['external'][str(x)]={'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()}
for x in sorted(p.rglob('*')):
 if x.is_file() and 'target' not in x.parts and x.name not in ['manifest.json','evidence.tar.gz','evidence.sha256']:manifest['files'][str(x.relative_to(p))]={'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()}
(p/'manifest.json').write_text(json.dumps(manifest,indent=2))
with tarfile.open(p/'evidence.tar.gz','w:gz') as t:
 for x in sorted(p.rglob('*')):
  if x.is_file() and 'target' not in x.parts and x.name not in ['evidence.tar.gz','evidence.sha256']:t.add(x,arcname=str(x.relative_to(p)))
(p/'evidence.sha256').write_text(hashlib.sha256((p/'evidence.tar.gz').read_bytes()).hexdigest()+'  evidence.tar.gz\n')
print((p/'evidence.sha256').read_text())
