"""Include the now-completed source-review log without changing circuit evidence."""
import hashlib,json,shutil,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();old=json.loads((r/'EVIDENCE-MANIFEST.json').read_text());receipt=json.loads((r/'PACKAGE-RESULT.json').read_text());assert sha(r/'final-evidence.tar.gz')==receipt['archive_sha256'];assert not(r/'final-evidence-before-review-log.tar.gz').exists();shutil.copyfile(r/'final-evidence.tar.gz',r/'final-evidence-before-review-log.tar.gz')
paths={}
for name in old['files']:
 parts=Path(name).parts
 if parts[0]in['gate','search','research']:
  folder={'gate':'breakthrough-public8b-repeat-final-gate-20261020','search':'breakthrough-public8b-repeat-nonce-20261020','research':'breakthrough-public8b-repeat-generic-20261020'}[parts[0]];p=r.parent/folder/Path(*parts[1:])
 else:p=r/name
 paths[name]=p
paths['repack-completed-log.py']=Path(__file__).resolve();audit={'reason':'Initial package captured source-review stdout before its final print. Repack after review completes, retaining the first archive on server. All source, gate, nonce and benchmark evidence unchanged.','previous_archive_sha256':receipt['archive_sha256']};(r/'PACKAGE-LOG-CORRECTION.json').write_text(json.dumps(audit,indent=2)+'\n');paths['PACKAGE-LOG-CORRECTION.json']=r/'PACKAGE-LOG-CORRECTION.json'
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{n:sha(p)for n,p in paths.items()},'scope':'Completed final source-review log plus unchanged full source, gate rows, nonce controls/screens and benchmark evidence; no resource-preflight or credentials.'},indent=2)+'\n')
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as a:
 for n,p in sorted(paths.items()):a.add(p,arcname=n,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(paths)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(len(paths)+1)
