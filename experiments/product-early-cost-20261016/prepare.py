from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'product-early-filter-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
