from pathlib import Path
import subprocess,json,hashlib,tarfile
root=Path(__file__).resolve().parent;dst=root/'observer-b3'
assert (root/'run.exit').read_text().strip()=='0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected={};mismatches=[]
for rel in subprocess.check_output(['git','-C',str(dst),'ls-files'],text=True).splitlines():
 if rel.startswith('src/point_add/'):continue
 data=subprocess.check_output(['git','-C',str(dst),'show','HEAD:'+rel])
 got=sha(dst/rel);expected=hashlib.sha256(data).hexdigest();protected[rel]={'disk':got,'base':expected}
 if got!=expected:mismatches.append(rel)
assert not mismatches,mismatches
patch=subprocess.check_output(['git','diff','--binary','HEAD'],cwd=dst)
for rel in subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=dst,text=True).splitlines():
 if not rel.startswith('src/point_add/'):continue
 p=subprocess.run(['git','diff','--no-index','--binary','--','/dev/null',rel],cwd=dst,capture_output=True);assert p.returncode in [0,1];patch+=p.stdout
(root/'observer-full.patch').write_bytes(patch)
(root/'protected-verification.json').write_text(json.dumps({'base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=dst,text=True).strip(),'matches':not mismatches,'files':protected},indent=2)+'\n')
with tarfile.open(root/'source-snapshots.tar.gz','w:gz')as tar:
 for name in ['observer-b3','window4-b3']:
  for p in (root/name/'src/point_add').rglob('*'):
   if p.is_file():tar.add(p,arcname=str(p.relative_to(root)))
with tarfile.open(root/'evidence.tar.gz','w:gz')as tar:
 for p in root.iterdir():
  if p.is_file() and p.name not in ['evidence.tar.gz','source-snapshots.tar.gz'] and p.suffix in ['.log','.json','.jsonl','.sha256','.patch','.exit','.pid','.py','.sh','.rs']:tar.add(p,arcname=p.name)
 for name in ['packets','superseded-reverse-tape','transition-observer','fold-startup-failure','forward-fold-observer','reverse-t0-observer','stage-observer']:
  if (root/name).exists():tar.add(root/name,arcname=name)
print(json.dumps({'protected_files':len(protected),'observer_patch_sha256':sha(root/'observer-full.patch'),'source_archive_sha256':sha(root/'source-snapshots.tar.gz'),'evidence_archive_sha256':sha(root/'evidence.tar.gz')},indent=2))
