from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
old=root.parent/'product-dispatch-filter-20261016'
tool=root/'tool'
assert not tool.exists(),'never overwrite a previous qualification tree'
shutil.copytree(old/'tool/src',tool/'src')
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
p=tool/'src/packed_body.rs';source=p.read_text()
for before,after in [
 ('180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64','268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d'),
 ('assert_eq!(n,14_142_629)','assert_eq!(n,17_891_821)')]:
 assert source.count(before)==1,(before,source.count(before))
 source=source.replace(before,after)
assert 'const PROOF_ACCEPTED:bool=false;' in source
p.write_text(source)
p=tool/'src/transfer.rs';source=p.read_text()
for before,after in [
 ('cache-certificate-v2-20261016','cache-certificate67-20261016'),
 ('4857f8255c6aa85f0c6cb84720c6d5690aaca060f2758a8c517bd43fc5e2f04e','303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6'),
 ('722be8db61c0a29533f3297a31192e64f7558d4c828b210c1b1dc33ce272c8b3','d774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f'),
 ('efc7c9583caf0d918fa555694a51aed9959b19c6b29fc198c2e82a8affc22317','5914f683bb5df08d21f94d79663c6239a84715e27b2eac7e18ce1fcafaee0167'),
 ('candidate180af069 universal25stage','candidate268aefe2 universal67stage')]:
 assert source.count(before)==1,(before,source.count(before))
 source=source.replace(before,after)
p.write_text(source)
