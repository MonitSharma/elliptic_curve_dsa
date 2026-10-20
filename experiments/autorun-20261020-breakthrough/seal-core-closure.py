import hashlib,json,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/breakthrough-core-closure-20261020');sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert (r/'run.exit').read_text().strip()=='0';f=json.loads((r/'MODEL-SOURCE-FREEZE.json').read_text())
assert not (r/'EVIDENCE-MANIFEST.json').exists()
files=[p for p in r.iterdir()if p.is_file() and p.name not in ['closure','resource-preflight.json']]
manifest={'files':{p.name:sha(p)for p in files},'binary_sha256':sha(r/'closure'),'scope':'Legacy inactive helper Boolean synthesis model only. No active-circuit improvement or native quantum construction.'}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p in files+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.name)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json'),'members':len(files)+1},indent=2)+'\n');print(len(files)+1,'members')
