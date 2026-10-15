"""Remove only the completed owned tree after full source/stream preservation."""
from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parent;e=root/'evidence';tree=root.parent/'product-exact-20261015/candidate-wide-compound'
assert tree==Path('/home/hclau/ecdsa_research/product-exact-20261015/candidate-wide-compound')
result=json.loads((root/'RESULT.json').read_text());assert result['status']=='COMPLETE_LOCAL_PASS_QUEUE_ELIGIBLE'
assert hashlib.sha256((e/'final-point-add-source.tar.gz').read_bytes()).hexdigest()==result['full_point_add_source_archive_sha256']
assert hashlib.sha256((e/'final-ops.bin').read_bytes()).hexdigest()==result['stream_sha256']
for name in ['protected.json','final-source.json']:
 for path,digest in json.loads((e/name).read_text()).items():assert hashlib.sha256((tree/path).read_bytes()).hexdigest()==digest,path
assert not subprocess.check_output(['git','-C',str(tree),'ls-files','--others','--exclude-standard'],text=True).strip()
for process in Path('/proc').iterdir():
 if not process.name.isdigit():continue
 for link in ['cwd','exe']:
  try:target=os.readlink(process/link)
  except OSError:continue
  assert target!=str(tree) and not target.startswith(str(tree)+'/'),(process.name,link,target)
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','remove','--force',str(tree)],check=True)
(e/'cleanup.json').write_text(json.dumps({'removed_worktree':str(tree),'source_archive_sha256':result['full_point_add_source_archive_sha256'],'preserved_stream_sha256':result['stream_sha256'],'source_rebuild':'fetch source_revision; detached worktree; apply evidence/final-candidate.patch; unchanged benchmark.sh'},indent=2)+'\n')
