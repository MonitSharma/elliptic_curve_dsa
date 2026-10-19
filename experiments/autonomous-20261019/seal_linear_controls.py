"""Seal successful primitive controls and the untouched pre-compiler refusal."""
import hashlib,io,json,os,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path(__file__).resolve().parent.parent;r=ws/'product-linear-witness-controls-v2-20261020';old=ws/'product-linear-witness-controls-20261020'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert (r/'run.exit').read_text().strip()=='0' and (old/'run.exit').read_text().strip()=='1' and not (old/'build-tests.log').exists()
result=json.loads((r/'RESULT.json').read_text());assert result['status']=='EXACT_LINEAR_WITNESS_30_PRIMITIVE_CONTROLS_PASS'
assert all(sha(r/p)==h for p,h in result['source_files'].items()) and all(sha(Path(p))==h for p,h in result['compiler_and_dependencies'].items())
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
data={}
for prefix,folder in [('',r),('failed-admission-v1/',old)]:
 for p in sorted(folder.iterdir()):
  if p.is_file() and p.suffix!='.bin' and not p.name.startswith(('evidence','EVIDENCE','LOCAL-VERIFICATION')):assert p.stat().st_size<1_000_000;data[prefix+p.name]=p.read_bytes()
for folder in [r,old]:
 desc=ws/'resource-registry-20261020'/(folder.name+'-run.json');data['registry/'+desc.name]=desc.read_bytes()
data['resource-profile.json']=(json.dumps(profile,indent=2)+'\n').encode()
files={k:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in data.items()}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'30 primitive controls pass, immutable source/compiler/direct-dependency hashes verified. V1 global-resource check refused before compiler due affinity ordering, preserved. No full-source scan, gate, nonce or score.', 'included_files':files,'test_binary_sha256':sha(r/'tests.bin')}
with tarfile.open(r/'evidence.tar.gz','x:gz') as a:
 for key,raw in data.items():m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
 raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'archive':'evidence.tar.gz','bytes':(r/'evidence.tar.gz').stat().st_size,'sha256':sha(r/'evidence.tar.gz'),'files':len(files),'scope':manifest['scope']},indent=2)+'\n');print((r/'EVIDENCE-MANIFEST.json').read_text())
