from pathlib import Path
import hashlib,json,tarfile
R=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
assert json.loads((R/'INDEPENDENT-REVIEW.json').read_text())['status']=='INDEPENDENT_TERMINAL_SOURCE_RECEIPT_ACCOUNTING_AND_COST_REVIEW_PASS'
files=[p for p in R.rglob('*')if p.is_file()and p.name not in('evidence.tar.gz','MANIFEST.json','ARCHIVE-RECEIPT.json')and'__pycache__'not in p.parts]
manifest={p.relative_to(R).as_posix():sha(p.read_bytes())for p in files}
(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(R/'evidence.tar.gz','w:gz')as tar:
 for p in sorted(files+[R/'MANIFEST.json']):tar.add(p,arcname=p.relative_to(R).as_posix())
with tarfile.open(R/'evidence.tar.gz')as tar:
 for name,h in manifest.items():assert sha(tar.extractfile(name).read())==h,name
receipt={'status':'ALL_LOCAL_REVIEW_EVIDENCE_ARCHIVE_MEMBERS_VERIFIED','archive_sha256':sha((R/'evidence.tar.gz').read_bytes()),'verified_members':len(manifest),'review_sha256':sha((R/'INDEPENDENT-REVIEW.json').read_bytes()),'final_census_source_review_sha256':sha((R/'FINAL-CENSUS-SOURCE-REVIEW.json').read_bytes())}
(R/'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
