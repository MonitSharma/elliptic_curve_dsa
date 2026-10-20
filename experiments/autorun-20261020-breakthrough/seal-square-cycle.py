"""Seal finished square research stages without build trees or streams."""
import hashlib,json,sys,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research')/sys.argv[1]
assert r.name in ['breakthrough-public322-square-generic-20261020','breakthrough-public322-square-lease-20261020','breakthrough-public322-square-finished-20261020','breakthrough-public322-square-final-gate-20261020']
assert(r/'run.exit').read_text().strip()=='0'and not(r/'EVIDENCE-MANIFEST.json').exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();files={}
if 'final-gate'in r.name:
 result=json.loads((r/'GATE-RESULT.json').read_text());assert result['verdict']=='FAILURE_RATE_GATE_PASS'and all(result['checks'].values());streams={key:result[key]for key in['candidate_stream_sha256','parent_stream_sha256']}
else:
 freeze=r/('SOURCE_FREEZE.json'if'lease'in r.name else'SOURCE-FREEZE.json');f=json.loads(freeze.read_text());t=r/('tool'if'lease'in r.name else'candidate')
 if 'lease'in r.name:
  for p,h in f['tool_source_files'].items():assert sha(t/p)==h;files['tool-source/'+p]=t/p
  assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
 else:
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
  with tarfile.open(r/'point-add-source.tar.gz','w:gz')as a:
   for p in sorted(f['source_files']):a.add(t/p,arcname=p,recursive=False)
 streams={p.relative_to(r).as_posix():sha(p)for p in list(r.glob('*.ops.bin'))+list(r.glob('*/ops.bin'))}
for p in r.iterdir():
 if p.is_file()and not p.name.endswith('.ops.bin')and'resource-preflight'not in p.name and p.name not in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:files[p.name]=p
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p:sha(v)for p,v in files.items()},'streams_retained_on_server':streams,'scope':'Immutable source, tests, logs and stream hashes. Raw and static counts remain diagnostic, not benchmark scores; final gate verdict preserved.'},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p,v in sorted(files.items()):a.add(v,arcname=p,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(r.name,len(files)+1)
