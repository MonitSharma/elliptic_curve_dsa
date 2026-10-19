"""Preserve complete finished footprint/boundary diagnostics, including large data."""
import hashlib,io,json,os,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path(__file__).resolve().parent.parent;sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
for name in ['product-lease-footprint-20261020','product-clean-lease-probe-20261020']:
 r=ws/name;assert (r/'run.exit').read_text().strip()=='0';result=json.loads((r/'RESULT.json').read_text());b=json.loads((r/'BINDING.json').read_text())
 assert all(sha(r/p)==h for p,h in b['source_files'].items())
 assert all(sha(Path(p))==h for p,h in b['compiler_and_direct_dependencies'].items())
 if name.startswith('product-clean'):
  base=json.loads((r/'base.json').read_text());probe=json.loads((r/'probe.json').read_text());probe.pop('lease_probe');assert probe==base
 else:assert sha(r/'FOOTPRINT.json')==result['footprint_sha256']
 files={};paths={}
 for p in sorted(r.iterdir()):
  if not p.is_file() or p.suffix=='.bin' or p.name.startswith(('evidence','EVIDENCE','LOCAL-VERIFICATION')):continue
  paths[p.name]=p;files[p.name]={'bytes':p.stat().st_size,'sha256':sha(p)}
 desc=ws/'resource-registry-20261020'/(name+'-run.json');paths['registry/'+desc.name]=desc;files['registry/'+desc.name]={'bytes':desc.stat().st_size,'sha256':sha(desc)}
 extra=(json.dumps(profile,indent=2)+'\n').encode();files['resource-profile.json']={'bytes':len(extra),'sha256':hashlib.sha256(extra).hexdigest()}
 manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Completed read-only top-wire/strong clean-boundary data with primitive and complete report/output controls. No lease implementation, width result, statistical gate, nonce or score. Large footprint JSON preserved losslessly inside archive.', 'included_files':files,'result':result}
 with tarfile.open(r/'evidence.tar.gz','x:gz',compresslevel=1) as a:
  for key,p in paths.items():a.add(p,arcname=key,recursive=False)
  m=tarfile.TarInfo('resource-profile.json');m.size=len(extra);a.addfile(m,io.BytesIO(extra))
  raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
 receipt={'archive':'evidence.tar.gz','bytes':(r/'evidence.tar.gz').stat().st_size,'sha256':sha(r/'evidence.tar.gz'),'files':len(files),'scope':manifest['scope']}
 (r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'directory':name,**receipt}),flush=True)
