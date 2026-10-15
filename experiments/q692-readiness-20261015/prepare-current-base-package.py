"""Package the full candidate point_add tree on the refreshed promoted base."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
source,store,dest,evidence=map(Path,sys.argv[1:5])
revision='441d9ef9f5fe05107f4390e9f623caffdf77349d'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(store),str(dest)],check=True)
# A historical object store can have no published refs; clone then omits
# its alternate even though the attested commit exists. Bind it explicitly.
alternate=dest/'.git/objects/info/alternates'
if not alternate.exists():
 assert subprocess.check_output(['git','-C',str(dest),'ls-files'])==b''
 alternate.parent.mkdir(parents=True,exist_ok=True)
 alternate.write_text(str(store.resolve()/'objects')+'\n',encoding='utf8')
subprocess.run(['git','-C',str(dest),'checkout','--detach',revision],check=True)
target=dest/'src/point_add'
assert target.resolve()==dest.resolve()/'src/point_add'
shutil.rmtree(target);shutil.copytree(source/'src/point_add',target)
# Preserve existing tracked executable modes and include every new source
# file in the reviewable patch. A plain working-tree diff omits new files.
for row in subprocess.check_output(['git','-C',str(dest),'ls-tree','-r','-z','HEAD','--','src/point_add/']).split(b'\0'):
 if not row:continue
 header,name=row.split(b'\t',1);mode=header.split()[0];p=dest/name.decode('utf8')
 if p.exists()and mode in [b'100644',b'100755']:p.chmod(0o755 if mode==b'100755'else 0o644)
subprocess.run(['git','-C',str(dest),'add','-A','--','src/point_add/'],check=True)
paths=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines()
assert paths and all(x.startswith('src/point_add/') for x in paths)
protected=[]
tracked=subprocess.check_output(['git','-C',str(dest),'ls-files','-z']).split(b'\0')
for raw in tracked:
 if not raw:continue
 name=raw.decode('utf8')
 if name.startswith('src/point_add/'):continue
 p=dest/name
 expected=subprocess.check_output(['git','-C',str(dest),'show','HEAD:'+name])
 assert p.read_bytes()==expected,name
 protected.append(dict(path=name,sha256=hashlib.sha256(expected).hexdigest()))
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary','--full-index','--cached','HEAD','--','src/point_add/'])
evidence.mkdir(exist_ok=True,parents=True)
(evidence/'current-base.patch').write_bytes(patch)
binding=dict(source_candidate=str(source),package=str(dest),base_revision=revision,changed_paths=paths,protected_files=protected,patch_sha256=hashlib.sha256(patch).hexdigest(),tree_sha=subprocess.check_output(['git','-C',str(dest),'write-tree'],text=True).strip(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(target.rglob('*'))if p.is_file()},status='PREPARED_UNSCORED_NOT_SUBMISSION_READY')
(evidence/'package-manifest.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:binding[k]for k in ['base_revision','changed_paths','patch_sha256','status']},indent=2))
