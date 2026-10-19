"""Build-only port. Never screens a nonce before the new final gate passes."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'product-classical-twelve-filter-20261019';n=ws/'product-copy-cache-native-20261020';proof=ws/'product-copy-cache-proof-20261020'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
native=json.loads((n/'NATIVE-RECEIPT.json').read_text());h=native['compressed_sha256']
assert h=='26dc60ee329a6cf448143eebc9f1f218efd73ffeaaef92213a75e7d31f3e7cc1'==sha(n/'candidate/ops.bin')
transfer=json.loads((proof/'TRANSFER.json').read_text());assert transfer['status']=='COPY_CACHE_VALUE_PHASE_AND_PHYSICAL_RNG_TRANSFER_AUDIT_PASS'
assert all(sha(Path(p))==v for p,v in transfer['required_artifacts'].items())
assert json.loads((old/'RESULT.json').read_text())['status']=='DISABLED_CLASSICAL_TWELVE_PIPELINE_QUALIFICATION_PASS'
tool=r/'tool';assert not tool.exists();shutil.copytree(old/'tool/src',tool/'src')
for name in ['Cargo.toml','Cargo.lock']:shutil.copy2(old/'tool'/name,tool/name)
before='17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7'
p=tool/'src/packed_body.rs';s=p.read_text()
for a,b in [(before,h),('assert_eq!(n,17_889_635)','assert_eq!(n,17_889_637)')]:assert s.count(a)==1;s=s.replace(a,b)
assert 'const PROOF_ACCEPTED:bool=false;' in s;p.write_text(s)
required=[proof/'TRANSFER.json',n/'SOURCE_FREEZE.json',n/'NATIVE-RECEIPT.json']
required.extend(Path(p) for p in transfer['required_artifacts'])
required=sorted(set(required));p=tool/'src/transfer.rs';s=p.read_text();needle='fn bind_transfer(){';assert s.count(needle)==1
extra=''.join(' sha_check('+json.dumps(str(p))+','+json.dumps(sha(p))+');\n' for p in required)
p.write_text(s.replace(needle,needle+'\n'+extra))
audit={}
for p in tool.rglob('*'):
    if not p.is_file():continue
    name=p.relative_to(tool).as_posix()
    if name not in ['src/packed_body.rs','src/transfer.rs']:assert p.read_bytes()==(old/'tool'/name).read_bytes(),name
    audit[name]={'sha256':sha(p),'scope':'candidate hash/opcount only' if name=='src/packed_body.rs' else 'append exact transfer bindings only' if name=='src/transfer.rs' else 'identical to qualified disabled parent4 filter'}
validate=(old/'validate.py').read_text()
needle="ops=Path('/home/hclau/ecdsa_research/product-classical-twelve-native-20261019/candidate/ops.bin')";assert validate.count(needle)==1
validate=validate.replace(needle,"ops=Path('/home/hclau/ecdsa_research/product-copy-cache-native-20261020/candidate/ops.bin')").replace(before,h).replace('DISABLED_CLASSICAL_TWELVE_PIPELINE_QUALIFICATION_PASS','DISABLED_COPY_CACHE_PIPELINE_QUALIFICATION_PASS')
(r/'validate.py').write_text(validate)
(r/'PREPARATION.json').write_text(json.dumps({'status':'SOURCE_BOUND_DISABLED_FILTER_BUILD_ONLY_NO_NONCE_TESTS_YET','candidate_stream_sha256':h,'original_filter':str(old),'files':audit,'additional_proof_artifacts':{str(p):sha(p) for p in required},'authoritative_rejection':False,'gate_required_before_validation':True,'validation_driver_sha256':sha(r/'validate.py')},indent=2)+'\n')
print('Source-bound disabled filter prepared; no nonce tested')
