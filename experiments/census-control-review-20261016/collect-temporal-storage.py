from pathlib import Path
import json,hashlib,tarfile,shutil
b=Path('/home/hclau/ecdsa_research');r=b/'n2-temporal-storage-20261016';s=b/'census-control-review-20261016';n='source-only-temporal-v1';d=r/n;assert not d.exists();d.mkdir();assert(s/'temporal-audit.exit').read_text().strip()=='0'
for name in['PREDECLARATION.json','RESULT.json','SUMMARY.json','summary.log']:shutil.copy2(r/name,d/name)
for name in['temporal-storage.py','summarize-temporal-storage.py','run-temporal-storage.sh','temporal-preflight.log','temporal-audit.log','temporal-audit.exit']:shutil.copy2(s/name,d/name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={str(p):sha(p)for p in[b/'current-value-attribution-20261016/attribution-checkpoint-v1.tar.gz',b/'n2-readonly-normalizers-20261016/source-only-readonly-v1.tar.gz']}
(d/'BASE-PINS.json').write_text(json.dumps(dict(depends_on=pins,source_family_and_four_exact_zero_slot_proofs_preserved_in_bases=True,no_candidate_or_sample=True,negative_scope='Strict unconditional-MR-origin holes, every q use fenced, original+returned loan slots excluded; six separate nonconstant slots, no independence or general no-qubit-repair claim'),indent=2)+'\n');external={str(p):dict(bytes=p.stat().st_size,sha256=sha(p),status='server-only, not archive member')for p in[b/'product-exact-20261015/tip/ops.bin']};files={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()};(d/'MANIFEST.json').write_text(json.dumps(dict(files=files,external=external,base_pins=pins),indent=2)+'\n');a=r/(n+'.tar.gz')
with tarfile.open(a,'w:gz')as tf:tf.add(d,arcname=n)
with tarfile.open(a)as tf:
 for name,v in files.items():data=tf.extractfile(n+'/'+name).read();assert len(data)==v['bytes']and hashlib.sha256(data).hexdigest()==v['sha256']
receipt=dict(status='PASS',archive=str(a),sha256=sha(a),bytes=a.stat().st_size,verified_members=len(files),external_server_only=len(external));(r/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
