from pathlib import Path
import json,hashlib,tarfile,io
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['prepare-seed-observer.py','inspect-seed-region.py','seed-region-diff.json','prepare-seed-candidate.py','prepare-seed-prefix.py','prepare-seed-protected.py','run-seed-prefix.sh']
j={'status':'REVIEWED_SOURCE_FAMILY_PREFIX_AND_PROTECTED_TEST_GENERATORS_PINNED',
 'review_sha256':sha(r/'REVIEW.json'),'sources':{n:sha(r/'source'/n)for n in names},
 'prior_review_archive_sha256':'2f71b35c4f8686dceb8154156424ee1b9be53fd7062bde7ff998e3a9bda09ccd'}
(r/'REVIEWED-GENERATOR-SOURCES.json').write_bytes((json.dumps(j,indent=2)+'\n').encode())
archive=r.parent/'evidence-seed-independent-review-v2.tar.gz';assert not archive.exists()
files=[p for p in r.rglob('*')if p.is_file()]
m={'status':'INDEPENDENT_SEED_SOURCE_REVIEW_WITH_REVIEWED_GENERATOR_SOURCES','files':[{'path':p.relative_to(r).as_posix(),'sha256':sha(p)}for p in sorted(files)]}
with tarfile.open(archive,'w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(m,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(archive)as t:
 for row in m['files']:assert hashlib.sha256(t.extractfile(row['path']).read()).hexdigest()==row['sha256']
print(json.dumps({'archive_sha256':sha(archive),'files':len(files),'generator_binding_sha256':sha(r/'REVIEWED-GENERATOR-SOURCES.json')}))
