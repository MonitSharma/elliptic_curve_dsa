from pathlib import Path
import hashlib,json,subprocess,tarfile
r=Path(__file__).resolve().parent;d=r/'preseed10-native67-20261016';tree=d/'candidate';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((r/'PRESEED10_FIXED67_FREEZE.json').read_text());native=tree/'ops.bin'
assert sha(native)==freeze['external_stream_sha256'];subprocess.run(['cmp',str(native),str(r/freeze['external_stream'])],check=True)
assert '4 passed; 0 failed' in (d/'loader-tests.log').read_text();assert '2 passed; 0 failed' in (d/'family-tests.log').read_text()
paths=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines();assert all(p.startswith('src/point_add/')for p in paths)
protected={}
for rel in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
 if rel.startswith('src/point_add/'):continue
 data=(tree/rel).read_bytes();assert data==subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+rel]);protected[rel]=hashlib.sha256(data).hexdigest()
files={p.relative_to(tree/'src/point_add').as_posix():sha(p)for p in (tree/'src/point_add').rglob('*')if p.is_file()}
with tarfile.open(d/'point-add-source.tar.gz','w:gz')as t:t.add(tree/'src/point_add',arcname='point_add')
receipt={'status':'PRESEED10_FIXED67_NATIVE_EXACT_FULL_BYTE_IDENTITY_AND_PROTECTED_SOURCE_PASS','native_stream_sha256':sha(native),'source_base_revision':freeze['base_revision'],'source_files_sha256':files,'protected_files_sha256':protected,'diff_paths':paths,'source_archive_sha256':sha(d/'point-add-source.tar.gz'),'preseed10_parent_receipt_sha256':sha(r/'preseed10-cache67-20261016/BASE_NATIVE_RECEIPT.json'),'fresh_cache_stage_receipts_sha256':sha(r/'preseed10-cache67-20261016/CACHE_STAGE_RECEIPTS.json'),'loader_tests':4,'family_tests':2,'fresh_census':'not launched','search_authority':False,'score':None}
certificate=r/'preseed10-cache67-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json';cert=json.loads(certificate.read_text());assert cert['candidate_stream_sha256']==sha(native)and cert['stage_count']==67
receipt['cache_certificate_sha256']=sha(certificate)
(d/'NATIVE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
