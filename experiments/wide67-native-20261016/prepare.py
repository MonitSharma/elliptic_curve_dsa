from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parent;dest=root/'wide67';dest.mkdir(exist_ok=True)
old=root.parent/'frozen-cache-table-20261016';up=root.parent/'product-exact-20261015'
freeze=json.loads((up/'WIDE67_FREEZE.json').read_text());prefix=freeze['prefix_manifest']
source=(old/'prepare.py').read_text()
replacements={
 'root=Path(__file__).resolve().parent':f'root=Path({str(dest)!r})',
 "up=root.parent/'product-exact-20261015'":"up=root.parent.parent/'product-exact-20261015'",
 "root.parent/'toffoli'":"root.parent.parent/'toffoli'",
 'PRODUCT25_FREEZE.json':'WIDE67_FREEZE.json','frozen_cache25':'frozen_cache_wide67',
 '4b2ec52fc55da796aa8f5ef851290297e8706424':'5a7c390233c72133df9b591c92e43422c5892142',
 "parent=up/'tip/ops.bin'":"parent=root.parent.parent/'nonce-screen-20261015/final-census/ops.bin'",
 'pn-96==11630620':'pn-96==10517907',
 'b200178da6b06e841e384f71c2562c54b1dec09e6ef0a1c44990d408dba4e2e2':'fb4704b5f36d9c9d2544c14a46bd661deacf7349b4340c489df6f8809e0e645a',
 'fn-96==14142533':f"fn-96=={prefix['pre_tail_ops']}",
 '24027e53f377f24195d290b5d343c519156cfa3ae45f64529def428a901f8480':prefix['pre_tail_sha3_256']}
for a,b in replacements.items():assert a in source,a;source=source.replace(a,b)
(dest/'frozen_cache.rs.in').write_text((old/'frozen_cache.rs.in').read_text().replace('frozen_cache25','frozen_cache_wide67'))
(dest/'generated-prepare.py').write_text(source);subprocess.run([sys.executable,str(dest/'generated-prepare.py')],check=True)
source=(root/'census-template.py').read_text();start=source.index("if name=='product53':");end=source.index("runner=root.parent/",start);source=source[:start]+source[end:]
source=source.replace("'32768','6'","'32768','2'");(root/'census.py').write_text(source)
