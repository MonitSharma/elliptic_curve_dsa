from pathlib import Path
import json,hashlib,tarfile,shutil
b=Path('/home/hclau/ecdsa_research');r=b/'n2-readonly-normalizers-20261016';e=b/'current-value-attribution-20261016';n='source-only-readonly-v1';d=r/n;assert not d.exists();d.mkdir();assert(r/'analysis.exit').read_text().strip()=='0'
for p in r.iterdir():
 if p.is_file()and p.suffix in['.json','.jsonl','.sha256','.log','.exit']:shutil.copy2(p,d/p.name)
for p in(r/'tool/src').rglob('*'):
 if p.is_file():q=d/p.relative_to(r);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in['Cargo.toml','Cargo.lock']:shutil.copy2(r/'tool'/name,d/'tool'/name)
shutil.copy2(r/'original-support-with-queries.rs',d/'original-support-with-queries.rs')
for name in['prepare-readonly-normalizers.py','run-readonly-normalizers.sh','analyze-readonly-normalizers.py']:shutil.copy2(e/name,d/name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();external={str(p):dict(bytes=p.stat().st_size,sha256=sha(p),status='preserved server-only, not archive member')for p in[b/'product-exact-20261015/tip/ops.bin',e/'target-tool/release/readonly_loans']};base=sha(e/'attribution-checkpoint-v1.tar.gz')
(d/'BASE-PIN.json').write_text(json.dumps(dict(attribution_checkpoint_v1_sha256=base,source_family='ALL source N2 loans; original actual-final bindings in checkpoint',negative_scope='No nonconstant target expressed by exact affine aliases/stable classical and existing inverse products under fixed caps. No arbitrary-pair or higher-degree exhaustion, no impossibility claim.',no_candidate_or_sampling=True),indent=2)+'\n')
files={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()};(d/'MANIFEST.json').write_text(json.dumps(dict(files=files,external=external,base_checkpoint_sha256=base),indent=2)+'\n');p=r/(n+'.tar.gz')
with tarfile.open(p,'w:gz')as tf:tf.add(d,arcname=n)
with tarfile.open(p)as tf:
 for f,v in files.items():x=tf.extractfile(n+'/'+f).read();assert len(x)==v['bytes']and hashlib.sha256(x).hexdigest()==v['sha256']
out=dict(status='PASS',archive=str(p),sha256=sha(p),bytes=p.stat().st_size,verified_members=len(files),external_server_only=len(external));(r/(n+'-receipt.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
