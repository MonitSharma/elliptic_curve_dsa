"""Export fully applicable patches, including deletion of old binary point data."""
from pathlib import Path
import hashlib,json,subprocess
root=Path('/home/hclau/ecdsa_research/q692_readiness_20261015')
for name,ev in [('package-control-fold-v3-r2','package-v3-r2-evidence'),('package-control-fold-v6','package-v6-evidence')]:
 package=root/name;evidence=root/ev
 for filename in ['current-base.patch','package-manifest.json']:
  p=evidence/filename;p.rename(evidence/('NONAPPLICABLE-'+filename))
 m=json.loads((evidence/'NONAPPLICABLE-package-manifest.json').read_text(encoding='utf8'))
 patch=subprocess.check_output(['git','-C',str(package),'diff','--binary','--full-index','--cached','HEAD','--','src/point_add/'])
 m['patch_sha256']=hashlib.sha256(patch).hexdigest();m['binary_patch_export']=True
 assert subprocess.check_output(['git','-C',str(package),'write-tree'],text=True).strip()==m['tree_sha']
 (evidence/'current-base.patch').write_bytes(patch)
 (evidence/'package-manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(package=name,patch_sha256=m['patch_sha256'],scope='binary-complete export; exact staged source tree unchanged')))
