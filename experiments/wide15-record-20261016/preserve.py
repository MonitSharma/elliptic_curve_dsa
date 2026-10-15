from pathlib import Path
import hashlib,json,shutil,tarfile
root=Path(__file__).resolve().parent;e=root/'evidence';tree=root.parent/'product-exact-20261015/candidate-wide-compound'
assert (root/'qualify.exit').read_text().strip()=='0'
assert (root/'after-audit.exit').read_text().strip()=='0'
result=json.loads((root/'RESULT.json').read_text());assert result['status']=='COMPLETE_LOCAL_PASS_QUEUE_ELIGIBLE'
assert json.loads((e/'prefix-audit.json').read_text())['status']=='PASS_only_identity_tail_changed'
for name in ['final-source.json','protected.json']:
 for path,digest in json.loads((e/name).read_text()).items():assert hashlib.sha256((tree/path).read_bytes()).hexdigest()==digest,path
with tarfile.open(e/'final-point-add-source.tar.gz','w:gz') as t:
 for p in sorted((tree/'src/point_add').rglob('*')):
  if p.is_file():t.add(p,arcname=str(p.relative_to(tree)))
shutil.copy2(tree/'ops.bin',e/'final-ops.bin')
assert hashlib.sha256((e/'final-ops.bin').read_bytes()).hexdigest()==result['stream_sha256']
result['nonce_tail_prefix_audit']=json.loads((e/'prefix-audit.json').read_text())
result['full_point_add_source_archive_sha256']=hashlib.sha256((e/'final-point-add-source.tar.gz').read_bytes()).hexdigest()
(root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print('all final sources, stream and protected files preserved')
