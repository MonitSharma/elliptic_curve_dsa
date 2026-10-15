"""Preserve the complete qualified source/stream before removing our worktree."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile
root=Path(__file__).resolve().parent;e=root/'evidence'
tree=root.parent/'product-exact-20261015/wide-candidate-final'
assert tree.resolve()==Path('/home/hclau/ecdsa_research/product-exact-20261015/wide-candidate-final')
result=json.loads((root/'RESULT.json').read_text());assert result['status']=='COMPLETE_LOCAL_PASS_QUEUE_ELIGIBLE'
for file in ['final-source.json','protected.json']:
 for p,h in json.loads((e/file).read_text()).items():assert hashlib.sha256((tree/p).read_bytes()).hexdigest()==h,p
assert hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()==result['stream_sha256']
untracked=subprocess.check_output(['git','-C',str(tree),'ls-files','--others','--exclude-standard'],text=True).splitlines()
assert all(p.startswith('src/point_add/') for p in untracked),untracked
with tarfile.open(e/'final-point-add-source.tar.gz','w:gz') as archive:
 for p in sorted((tree/'src/point_add').rglob('*')):
  if p.is_file():archive.add(p,arcname=str(p.relative_to(tree)))
shutil.copy2(tree/'ops.bin',e/'final-ops.bin')
assert hashlib.sha256((e/'final-ops.bin').read_bytes()).hexdigest()==result['stream_sha256']
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','remove','--force',str(tree)],check=True)
(e/'cleanup.json').write_text(json.dumps({'removed_worktree':str(tree),'point_add_source_archive_sha256':hashlib.sha256((e/'final-point-add-source.tar.gz').read_bytes()).hexdigest(),'preserved_stream_sha256':result['stream_sha256'],'source_rebuild':'fetch base_revision; detached worktree; apply evidence/final-candidate.patch; unchanged benchmark.sh'},indent=2)+'\n')
