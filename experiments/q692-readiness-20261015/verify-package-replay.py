"""Replay the complete exported patch in a pristine promoted-base checkout."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path('/home/hclau/ecdsa_research/q692_readiness_20261015')
version=sys.argv[1];ev=root/f'package-{version}-evidence';m=json.loads((ev/'package-manifest.json').read_text(encoding='utf8'))
store=Path('/home/hclau/ecdsa_research/overnight-20261014/product-leader441d-final-objectstore')
suffix='-'+sys.argv[2]if len(sys.argv)>2 else''
dest=root/f'clean-replay-{version}{suffix}';assert not dest.exists()
subprocess.run(['git','init',str(dest)],check=True,stdout=subprocess.DEVNULL)
alt=dest/'.git/objects/info/alternates';alt.parent.mkdir(parents=True,exist_ok=True);alt.write_text(str(store/'objects')+'\n',encoding='utf8')
subprocess.run(['git','-C',str(dest),'checkout','--detach',m['base_revision']],check=True,stdout=subprocess.DEVNULL)
patch=ev/'current-base.patch';assert hashlib.sha256(patch.read_bytes()).hexdigest()==m['patch_sha256']
subprocess.run(['git','-C',str(dest),'apply','--whitespace=nowarn','--index',str(patch)],check=True)
tree=subprocess.check_output(['git','-C',str(dest),'write-tree'],text=True).strip();assert tree==m['tree_sha']
for relative,expected in m['source_sha256'].items():assert hashlib.sha256((dest/relative).read_bytes()).hexdigest()==expected,relative
for entry in m['protected_files']:assert hashlib.sha256((dest/entry['path']).read_bytes()).hexdigest()==entry['sha256'],entry['path']
assert subprocess.check_output(['git','-C',str(dest),'diff','--name-only'])==b''
changed=subprocess.check_output(['git','-C',str(dest),'diff','--cached','HEAD','--name-only'],text=True).splitlines()
assert changed==m['changed_paths']and all(x.startswith('src/point_add/')for x in changed)
receipt=dict(status='CLEAN_REPLAY_PASS',base_revision=m['base_revision'],package=str(dest),patch_sha256=m['patch_sha256'],tree_sha=tree,point_add_files=len(m['source_sha256']),protected_files=len(m['protected_files']),changed_paths=len(changed),scope='complete point_add patch applied to pristine promoted base; exact source content and protected files match')
(ev/'clean-replay-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt,indent=2))
