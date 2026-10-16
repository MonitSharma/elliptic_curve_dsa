from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent;h=lambda b:hashlib.sha256(b).hexdigest()
assert(r/'evidence/mask-cones-v1.exit').read_text().strip()=='0'
assert(r/'evidence/mask-cones-v1-before.sha256').read_bytes()==(r/'evidence/mask-cones-v1-after.sha256').read_bytes()
files={Path(__file__).resolve(),r/'tool/src/bin/mask_cone_census.rs',r/'run-mask-cones-v1.sh',r/'mask-cone-root-summary.py',r/'mask-cones-v1-report.md'}|set(r.glob('evidence/mask-cones-v1*'))|{r/'evidence/mask-cones-root-summary-v1.json'}
rows=[];data=[]
for p in sorted(files):
 if not p.is_file():continue
 b=p.read_bytes();name=str(p.relative_to(r));rows.append(dict(path=name,sha256=h(b),size=len(b)));data.append((name,b))
refs=[]
for name in['tool/target/release/mask_cone_census','evidence/mr-mask-tip-v3.bin']:
 p=r/name;b=p.read_bytes();refs.append(dict(path=str(p),sha256=h(b),size=len(b)))
manifest=dict(status='SOURCE_ONLY_CONE_NEGATIVE_ALL_IDENTITY_CHECKS_PASS',files=rows,server_only_refs=refs)
p=r/'evidence-mask-cones-supplement.tar.gz'
with tarfile.open(p,'w:gz')as t:
 for name,b in data:
  i=tarfile.TarInfo(name);i.size=len(b);t.addfile(i,io.BytesIO(b))
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(p)as t:
 for row in rows:assert h(t.extractfile(row['path']).read())==row['sha256']
receipt=dict(status='ALL_MANIFEST_ENTRIES_VERIFY',archive=p.name,sha256=h(p.read_bytes()),files=len(rows),server_refs=len(refs))
(r/'evidence/mask-cones-archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
