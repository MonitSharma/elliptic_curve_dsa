"""Rebind the qualified PRODUCT67 filter tool to the frozen PRODUCT95 stream and its universal95 certificate.

Only candidate hash, op count, certificate directory and the certificate/companion hashes change.
Hashes of the companion files are read from the completed cache-certificate95 directory.
"""
from pathlib import Path
import hashlib,shutil,sys
root=Path(__file__).resolve().parent
old=root.parent/'product67-filter-20261016'
cert=root.parent/'product-exact-20261015/cache-certificate95-20261017'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=root/'tool'
assert not tool.exists(),'never overwrite a previous qualification tree'
shutil.copytree(old/'tool/src',tool/'src')
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
p=tool/'src/packed_body.rs';source=p.read_text()
for before,after in [
 ('268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d','ba87b9ceb0691ccfe8c509539cfc38e774ee02134363c19e3541c6e942723e84'),
 ('assert_eq!(n,17_891_821)','assert_eq!(n,20_275_836)')]:
 assert source.count(before)==1,(before,source.count(before))
 source=source.replace(before,after)
assert 'const PROOF_ACCEPTED:bool=false;' in source
p.write_text(source)
p=tool/'src/transfer.rs';source=p.read_text()
for before,after in [
 ('cache-certificate67-20261016','cache-certificate95-20261017'),
 ('303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6',sha(cert/'CACHE_EQUIVALENCE_CERTIFICATE.json')),
 ('d774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f',sha(cert/'PER_INPUT_MASK_TRANSFER.json')),
 ('5914f683bb5df08d21f94d79663c6239a84715e27b2eac7e18ce1fcafaee0167',sha(cert/'PER_INPUT_MASK_TRANSFER.md')),
 ('candidate268aefe2 universal67stage','candidateba87b9ce universal95stage')]:
 assert source.count(before)==1,(before,source.count(before))
 source=source.replace(before,after)
p.write_text(source)
print('PREPARED_PRODUCT95_FILTER_TOOL')
