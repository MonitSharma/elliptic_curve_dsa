from pathlib import Path
import json,hashlib,tarfile,shutil,subprocess
r=Path('/home/hclau/ecdsa_research/seed-restore-20261016');b=r.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();d=r/'terminal-v1';assert not d.exists();assert(r/'qualification.exit').read_text().strip()=='0'
assert sha(r/'PREDECLARATION.json')=='98ccedaa3eaed8efa99458d2daa84aa7968d3e19ee765855aa47d606c30115c6';assert sha(r/'candidate/ops.bin')=='a996cf16d64b11a20cb9a56d0688d034153f843751f640ea7113f50739c20608';assert sha(b/'product-exact-20261015/tip/ops.bin')=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
for line in (r/'seed-fresh/source-checker.sha256').read_text().splitlines():
 digest,path=line.split(maxsplit=1);p=Path(path);p=p if p.is_absolute()else r/p;assert sha(p)==digest,path
d.mkdir();shutil.copytree(r/'seed-fresh',d/'seed-fresh')
names=['PREDECLARATION.json','source-files.json','source.patch','native-verification.json','native-verification.log','native-verification.exit','native.log','native.exit','native-build.log','native-build.exit','guard-tests.log','guard-tests.exit','protected.log','protected.exit','protected-build.log','protected-build.exit','protected-prepare.log','protected-prepare.exit','qualification-launch.log','qualification.exit','paired-summary.json','paired-summary.log','paired-summary.exit','summarize-seed-paired.py','verify-seed-stream-server.py','collect-terminal.py','seed_restore.rs','seed_restore.bin']
for name in names:shutil.copy2(r/name,d/name)
checker=b/'failure-census-20261015/census';shutil.copytree(checker/'src',d/'checker-src');shutil.copy2(checker/'Cargo.toml',d/'checker-Cargo.toml')
if(checker/'Cargo.lock').exists():shutil.copy2(checker/'Cargo.lock',d/'checker-Cargo.lock')
shutil.copy2(b/'failure-census-20261015/target/release/failure_census',d/'failure_census')
base=[r/'native-source-freeze-v1.tar.gz',b/'current-value-attribution-20261016/seed-diagnosis-v1.tar.gz'];pins={str(p):sha(p)for p in base};(d/'BASE-PINS.json').write_text(json.dumps(pins,indent=2)+'\n')
external={str(p):dict(sha256=sha(p),bytes=p.stat().st_size,status='server-only, not archive member')for p in[r/'candidate/ops.bin',b/'product-exact-20261015/tip/ops.bin']};files={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()};(d/'MANIFEST.json').write_text(json.dumps(dict(files=files,base_pins=pins,external=external,runtime_checker_and_sources_before_after_SHA_pass=True),indent=2)+'\n');a=r/'terminal-v1.tar.gz'
with tarfile.open(a,'w:gz')as tf:tf.add(d,arcname=d.name)
with tarfile.open(a)as tf:
 for name,v in files.items():data=tf.extractfile(d.name+'/'+name).read();assert len(data)==v['bytes']and hashlib.sha256(data).hexdigest()==v['sha256']
receipt=dict(status='PASS',archive=str(a),sha256=sha(a),verified_members=len(files),external_streams=len(external));(r/'terminal-v1-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
