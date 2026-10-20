import hashlib,json,sys,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research')/sys.argv[1];assert r.name in['breakthrough-prefix27-room-grid-20261020','breakthrough-prefix-xag-resynth-20261020'];assert(r/'run.exit').read_text().strip()=='0';assert not(r/'EVIDENCE-MANIFEST.json').exists();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files=[p for p in r.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.name!='ops.bin'and not p.name.endswith('.ops.bin')and'resource-preflight'not in p.name]
audit={'status':'COMPLETED_RESEARCH_ONLY_NOT_BENCHMARK','stream_hashes':{p.relative_to(r).as_posix():sha(p)for p in r.glob('*/ops.bin')},'scope':'Preserve fixed grid or finite exact synthesis outcomes with all input/source/log hashes. No gate, nonce or resource record. Unsuccessful solver statuses remain incomplete results, not lower bounds.'};(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');files.append(r/'TERMINAL-AUDIT.json')
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':audit},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p in files+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(r.name,len(files)+1)
