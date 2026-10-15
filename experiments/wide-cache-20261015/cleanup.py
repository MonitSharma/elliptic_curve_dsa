"""Archive our terminal failed candidate before removing its detached tree."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile
root=Path(__file__).resolve().parent;tree=root/'candidate';e=root/'evidence'
assert tree.resolve()==Path('/home/hclau/ecdsa_research/wide-cache-20261015/candidate')
assert hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()=='b20532dcfb14b568fc7224f978b0b585b2c880725e2b9cf6592a23bdbc8981d2'
changed=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines()
untracked=subprocess.check_output(['git','-C',str(tree),'ls-files','--others','--exclude-standard'],text=True).splitlines()
assert all(p.startswith('src/point_add/') for p in changed+untracked)
patch=subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add'])
for p in untracked:
 r=subprocess.run(['git','diff','--no-index','/dev/null',p],cwd=tree,capture_output=True);assert r.returncode==1;patch+=r.stdout
(e/'cleanup-candidate.patch').write_bytes(patch)
manifest={str(p.relative_to(tree)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (tree/'src/point_add').rglob('*') if p.is_file()}
(e/'cleanup-source.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(e/'cleanup-point-add-source.tar.gz','w:gz') as t:
 for p in sorted((tree/'src/point_add').rglob('*')):
  if p.is_file():t.add(p,arcname=str(p.relative_to(tree)))
shutil.copy2(tree/'ops.bin',e/'unqualified-ops.bin')
assert hashlib.sha256((e/'unqualified-ops.bin').read_bytes()).hexdigest()=='b20532dcfb14b568fc7224f978b0b585b2c880725e2b9cf6592a23bdbc8981d2'
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','remove','--force',str(tree)],check=True)
(e/'cleanup.json').write_text(json.dumps({'removed':str(tree),'status':'failed_presearch_gate_no_nonce','stream_sha256':'b20532dcfb14b568fc7224f978b0b585b2c880725e2b9cf6592a23bdbc8981d2','source_archive_sha256':hashlib.sha256((e/'cleanup-point-add-source.tar.gz').read_bytes()).hexdigest()},indent=2)+'\n')
