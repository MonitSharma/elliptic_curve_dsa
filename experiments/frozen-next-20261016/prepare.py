"""Reuse the admitted source-bound static loader for fixed product53/wide43 outputs."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path(__file__).resolve().parent
name=sys.argv[1];assert name in ['product53','wide43']
dest=root/name;dest.mkdir(exist_ok=True)
old=root.parent/'frozen-cache-table-20261016'
source=(old/'prepare.py').read_text()
freeze_path=root.parent/'product-exact-20261015'/('PRODUCT53_FREEZE.json' if name=='product53' else 'WIDE43_FREEZE.json')
freeze=json.loads(freeze_path.read_text());prefix=freeze['prefix_manifest']
replacements={
 'root=Path(__file__).resolve().parent':f'root=Path({str(dest)!r})',
 "up=root.parent/'product-exact-20261015'":"up=root.parent.parent/'product-exact-20261015'",
 "root.parent/'toffoli'":"root.parent.parent/'toffoli'",
 'PRODUCT25_FREEZE.json':freeze_path.name,
 'frozen_cache25':'frozen_cache_'+name,
 "fn-96==14142533":f"fn-96=={prefix['pre_tail_ops']}",
 '24027e53f377f24195d290b5d343c519156cfa3ae45f64529def428a901f8480':prefix['pre_tail_sha3_256'],
}
if name=='wide43':
 replacements.update({
  '4b2ec52fc55da796aa8f5ef851290297e8706424':'5a7c390233c72133df9b591c92e43422c5892142',
  "parent=up/'tip/ops.bin'":"parent=root.parent.parent/'nonce-screen-20261015/final-census/ops.bin'",
  'pn-96==11630620':'pn-96==10517907',
  'b200178da6b06e841e384f71c2562c54b1dec09e6ef0a1c44990d408dba4e2e2':'fb4704b5f36d9c9d2544c14a46bd661deacf7349b4340c489df6f8809e0e645a',
 })
for a,b in replacements.items():assert a in source,a;source=source.replace(a,b)
template=(old/'frozen_cache.rs.in').read_text().replace('frozen_cache25','frozen_cache_'+name)
(dest/'frozen_cache.rs.in').write_text(template)
(dest/'generated-prepare.py').write_text(source)
subprocess.run([sys.executable,str(dest/'generated-prepare.py')],check=True)
