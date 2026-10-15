from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'product-mask-filter-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
source=(tool/'src/packed_body.rs').read_text()
assert source.count('count<=4096')==1 and source.count('threads<=32')==1
source=source.replace('count<=4096','count<=65536').replace('threads<=32','threads<=12')
(tool/'src/packed_body.rs').write_text(source)
