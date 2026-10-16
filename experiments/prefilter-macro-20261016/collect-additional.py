from pathlib import Path
import hashlib,json,tarfile,shutil,subprocess
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');dest=root/'additional/independent-proof-receipts';dest.mkdir(exist_ok=True)
pref=root.parent/'prefilter-20261015'
for name in['reset-projection-carry.summary.json','reset-projection-carry.jsonl','shadow-value-complete-helpers.json','shadow-value-carry.json','shadow-value-zeros-carry.json']:
 p=pref/'evidence'/name
 if p.exists():shutil.copy2(p,dest/name)
names=['STATUS-ADDITIONAL.md','collect-additional.py','map-residual-sites.py','prepare-carry-helper.py','run-carry-helper.sh','bind-carry-helpers.py','inspect-opaque-helper.py','map-context-anchors.py','prepare-complete-helpers.py','run-complete-helpers.sh','bind-complete-helpers.py','normalize-bitids.c','normalize-bitids.so','bind-phase-lifetimes.py','bind-expanded-lifetimes.py','bind-opaque-closure.py','trace-opaque-wires.py','opaque-cleanup-epochs.py']
paths=[root/p for p in names]+[p for p in(root/'additional').rglob('*')if p.is_file()]
files={str(p.relative_to(root)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in paths}
external={}
for p in[root/'raw-builder.bin',root.parent/'product-exact-20261015/tip/ops.bin']:
 external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only; not an archive member')
manifest=dict(files=files,external=external,prior_archive_sha256='9e7ad842c43356a7f34d1976e76b1750558ed2672cc802db17620c053ea4ff40')
m=root/'additional-manifest.json';m.write_text(json.dumps(manifest,indent=2)+'\n');paths.append(m)
archive=root/'additional-evidence.tar.gz'
with tarfile.open(archive,'w:gz')as t:
 for p in sorted(paths):t.add(p,arcname=str(p.relative_to(root)),recursive=False)
digest=hashlib.sha256(archive.read_bytes()).hexdigest();(root/'additional-evidence.sha256').write_text(digest+'  additional-evidence.tar.gz\n');print(digest,len(files),len(external),archive.stat().st_size)
