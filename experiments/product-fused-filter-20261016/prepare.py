from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'product-mask-filter-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
shutil.copyfile(root/'masks.rs',tool/'src/masks.rs')
body=(tool/'src/packed_body.rs').read_text();assert body.count('count<=4096')==1;body=body.replace('count<=4096','count<=65536');(tool/'src/packed_body.rs').write_text(body)
