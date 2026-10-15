"""Preserve and repair incomplete draft exports; source contents are unchanged."""
from pathlib import Path
import hashlib,json,subprocess
root=Path('/home/hclau/ecdsa_research/q692_readiness_20261015')
for name,ev in [('package-control-fold-v3-r2','package-v3-r2-evidence'),('package-control-fold-v6','package-v6-evidence')]:
 package=root/name;evidence=root/ev
 for filename in ['current-base.patch','package-manifest.json']:
  p=evidence/filename;p.rename(evidence/('INCOMPLETE-'+filename))
 m=json.loads((evidence/'INCOMPLETE-package-manifest.json').read_text(encoding='utf8'))
 for relative,expected in m['source_sha256'].items():assert hashlib.sha256((package/relative).read_bytes()).hexdigest()==expected,relative
 for row in subprocess.check_output(['git','-C',str(package),'ls-tree','-r','-z','HEAD','--','src/point_add/']).split(b'\0'):
  if not row:continue
  header,relative=row.split(b'\t',1);mode=header.split()[0];p=package/relative.decode('utf8')
  if p.exists()and mode in [b'100644',b'100755']:p.chmod(0o755 if mode==b'100755'else 0o644)
 subprocess.run(['git','-C',str(package),'add','-A','--','src/point_add/'],check=True)
 patch=subprocess.check_output(['git','-C',str(package),'diff','--cached','HEAD','--','src/point_add/'])
 changed=subprocess.check_output(['git','-C',str(package),'diff','--cached','HEAD','--name-only'],text=True).splitlines()
 assert all(x.startswith('src/point_add/')for x in changed)
 for relative,expected in m['source_sha256'].items():
  assert hashlib.sha256(subprocess.check_output(['git','-C',str(package),'show',':'+relative])).hexdigest()==expected,relative
 for entry in m['protected_files']:assert hashlib.sha256((package/entry['path']).read_bytes()).hexdigest()==entry['sha256'],entry['path']
 m.update(changed_paths=changed,patch_sha256=hashlib.sha256(patch).hexdigest(),tree_sha=subprocess.check_output(['git','-C',str(package),'write-tree'],text=True).strip(),repair='Include all new point_add files and preserve existing modes; no source content changed')
 (evidence/'current-base.patch').write_bytes(patch)
 (evidence/'package-manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(package=name,changed_paths=len(changed),new_patch_sha256=m['patch_sha256'],tree_sha=m['tree_sha'],scope='draft export repaired; source bytes and generated circuit unchanged')))
