"""Seal the completed prefix/rank diagnostic; never treat it as a width bound."""
import hashlib,io,json,os,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path(__file__).resolve().parent.parent;r=ws/'product-peak-parity-probe-20261020';sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert (r/'run.exit').read_text().strip()=='0';b=json.loads((r/'BINDING.json').read_text());result=json.loads((r/'RESULT.json').read_text())
assert result['status']=='EXACT_CONSERVATIVE_PEAK_ANF_RANK_DIAGNOSTIC_COMPLETED'
assert (r/'base.json').read_bytes()==(r/'probe.json').read_bytes()
assert all(sha(r/p)==h for p,h in b['source_files'].items())
assert all(sha(Path(p))==h for p,h in b['compiler_and_direct_dependencies'].items())
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
files={};paths={}
for p in sorted(r.iterdir()):
 if not p.is_file() or p.suffix=='.bin' or p.name.startswith(('evidence','EVIDENCE','LOCAL-VERIFICATION')):continue
 paths[p.name]=p;files[p.name]={'bytes':p.stat().st_size,'sha256':sha(p)}
desc=ws/'resource-registry-20261020'/(r.name+'-run.json');paths['registry/'+desc.name]=desc;files['registry/'+desc.name]={'bytes':desc.stat().st_size,'sha256':sha(desc)}
extra=(json.dumps(profile,indent=2)+'\n').encode();files['resource-profile.json']={'bytes':len(extra),'sha256':hashlib.sha256(extra).hexdigest()}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Completed17+17 controls, prefix metadata/hash/counter equality and two independent universal-ANF snapshots. Exact conservative rank is full1233, no linear relation at this fixed first peak; not a physical-width lower bound, lease or record.', 'included_files':files,'binary_hashes':{name:sha(r/(name+'.bin')) for name in ['base','probe']}}
with tarfile.open(r/'evidence.tar.gz','x:gz') as a:
 for key,p in paths.items():a.add(p,arcname=key,recursive=False)
 m=tarfile.TarInfo('resource-profile.json');m.size=len(extra);a.addfile(m,io.BytesIO(extra))
 raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'archive':'evidence.tar.gz','bytes':(r/'evidence.tar.gz').stat().st_size,'sha256':sha(r/'evidence.tar.gz'),'files':len(files),'scope':manifest['scope']},indent=2)+'\n');print((r/'EVIDENCE-MANIFEST.json').read_text())
