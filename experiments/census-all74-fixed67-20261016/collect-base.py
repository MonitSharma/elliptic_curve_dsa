from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path(__file__).resolve().parent;d=r/'all74-cache67-20261016';out=d/'native-base-evidence-v1';assert(d/'base-launcher.exit').read_text().strip()=='0';out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['DECLARATION.json','base-source.patch','base-source-files.json','BASE_NATIVE_RECEIPT.json','base-preflight.json','base-prepare.log','base-tests.log','base-build.log','base-generate.log','base-verification.log','base-stream.sha256','base-launcher.pid','base-launcher.exit']:
 shutil.copy2(d/name,out/name)
for name in ['prepare_all74_base.py','verify_all74_base.py','run-all74-base.sh','collect-base.py','PRODUCT67_FREEZE.json','TEMPLATE-PINS.json']:
 shutil.copy2(r/name,out/name)
shutil.copytree(d/'base-point-add-source',out/'point_add')
receipt=json.loads((d/'BASE_NATIVE_RECEIPT.json').read_text());assert sha(r/'candidate-all74-base/ops.bin')==receipt['source_sha256'];assert{p.relative_to(out/'point_add').as_posix():sha(p)for p in(out/'point_add').rglob('*')if p.is_file()}==receipt['source_files_sha256']
base=r.parent/'census-deletion-family-20261016/source-only-v1.tar.gz';pins={str(base):sha(base)};external={str(p):dict(bytes=p.stat().st_size,sha256=sha(p),status='server-only, not archive member')for p in[r/'candidate-all74-base/ops.bin',r.parent/'payload-model-20261016/before-census.bin',r.parent/'product-exact-20261015/tip/ops.bin']};files={str(p.relative_to(out)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()};(out/'MANIFEST.json').write_text(json.dumps(dict(files=files,base_pins=pins,external=external),indent=2)+'\n');a=d/'native-base-evidence-v1.tar.gz'
with tarfile.open(a,'w:gz')as tf:tf.add(out,arcname=out.name)
with tarfile.open(a)as tf:
 for name,v in files.items():data=tf.extractfile(out.name+'/'+name).read();assert len(data)==v['bytes']and hashlib.sha256(data).hexdigest()==v['sha256']
result=dict(status='PASS',archive=str(a),sha256=sha(a),verified_members=len(files),external_streams=len(external));(d/'native-base-evidence-v1-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
