from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parent;dest=root/'product67';dest.mkdir(exist_ok=True)
old=root.parent/'frozen-cache-table-20261016';up=root.parent/'product-exact-20261015'
freeze=json.loads((up/'PRODUCT67_FREEZE.json').read_text());prefix=freeze['prefix_manifest']
source=(old/'prepare.py').read_text()
replacements={
 'root=Path(__file__).resolve().parent':f'root=Path({str(dest)!r})',
 "up=root.parent/'product-exact-20261015'":"up=root.parent.parent/'product-exact-20261015'",
 "root.parent/'toffoli'":"root.parent.parent/'toffoli'",
 'PRODUCT25_FREEZE.json':'PRODUCT67_FREEZE.json','frozen_cache25':'frozen_cache_product67',
 'fn-96==14142533':f"fn-96=={prefix['pre_tail_ops']}",
 '24027e53f377f24195d290b5d343c519156cfa3ae45f64529def428a901f8480':prefix['pre_tail_sha3_256']}
for a,b in replacements.items():assert a in source,a;source=source.replace(a,b)
(dest/'frozen_cache.rs.in').write_text((old/'frozen_cache.rs.in').read_text().replace('frozen_cache25','frozen_cache_product67'))
(dest/'generated-prepare.py').write_text(source);subprocess.run([sys.executable,str(dest/'generated-prepare.py')],check=True)
# Reuse the audited fixed-census implementation, removing only its obsolete
# duplicate product53 routing. The new sample/label is fixed before launch.
source=(root/'census-template.py').read_text();start=source.index("if name=='product53':");end=source.index("runner=root.parent/",start)
source=source[:start]+source[end:];source=source.replace("if name=='product53' else", "if name=='product67' else")
(root/'census.py').write_text(source)
