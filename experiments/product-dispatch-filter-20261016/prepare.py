from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'product-early-filter-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
source=(tool/'src/packed_body.rs').read_text()
needle='let lib=format!("{root}/libzero8_slice.so");sha_check(&lib,"84b73bcdee01bb537d0320f9985a682758d1076860455ad382a2ae175690ea82");'
assert source.count(needle)==1
replacement='let fast=std::env::var_os("FAST_ZERO_DISPATCH").is_some();let lib=if fast{"/home/hclau/ecdsa_research/zero-dispatch-20261016/libthreaded.so".to_string()}else{format!("{root}/libzero8_slice.so")};sha_check(&lib,if fast{"1444e146e9359940123af3b951069c768313947f601d201b4bc391d8ac45cb95"}else{"84b73bcdee01bb537d0320f9985a682758d1076860455ad382a2ae175690ea82"});'
source=source.replace(needle,replacement)
assert 'const PROOF_ACCEPTED:bool=false;' in source
(tool/'src/packed_body.rs').write_text(source)
