"""Independently inspect the actual14 new universal stage logs and source chain."""
from pathlib import Path,PurePosixPath
import gzip,hashlib,json,re,tarfile
root=Path(__file__).resolve().parents[2]/'experiments/product-exact-20261015'
sha=lambda b:hashlib.sha256(b).hexdigest()
base_path=root/'evidence.tar.gz'
prior_path=root/'supplement-repaired67-qualified-20261016.tar.gz'
next_path=root/'supplement-finalproof95-endpoint-20261016.tar.gz'
assert sha(base_path.read_bytes())=='aa137f820aad142765c2d56ef0aa582cdc451fc5ea0cb3a7d564f4a8c6ebcf96'
assert sha(prior_path.read_bytes())=='9ec9889206393fd00ee7188c969c5fcdeffe6b23e34673acb9ba93dec047561e'
assert sha(next_path.read_bytes())=='97be8c18510792140822ff6c6fe134f36500b1602feede058ab6c13110ddcf5d'
with tarfile.open(base_path) as base,tarfile.open(prior_path) as prior,tarfile.open(next_path) as followup:
    for archive in [base,prior,followup]:
        names=archive.getnames();assert len(names)==len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert all(m.isfile() or m.isdir() for m in archive.getmembers())
    oldm=json.load(prior.extractfile('increment/manifest.json'))
    oldr=json.load(prior.extractfile('increment/current-receipt.json'))
    newm=json.load(followup.extractfile('followup/manifest.json'))
    newr=json.load(followup.extractfile('followup/current-receipt.json'))
    def oldread(name):
        if name in oldm['stored_new_or_changed_paths']:data=prior.extractfile('increment/artifacts/'+name).read()
        elif name in oldm.get('exact_gzip_mtime_byte_patches',{}):
            p=oldm['exact_gzip_mtime_byte_patches'][name];data=base.extractfile('evidence/'+p['base_path']).read();data=data[:4]+bytes.fromhex(p['mtime_bytes_hex'])+data[8:]
        else:data=base.extractfile('evidence/'+oldm['copy_from_base_artifact_path'].get(name,name)).read()
        assert sha(data)==oldr['files'][name],name
        return data
    def read(name):
        if name not in newr['files'] and name+'.gz' in newr['files']:return gzip.decompress(read(name+'.gz'))
        if name in newm['stored_new_or_changed_paths']:data=followup.extractfile('followup/artifacts/'+name).read()
        else:data=oldread(newm['copy_from_verified_logical_base_path'].get(name,name))
        assert sha(data)==newr['files'][name],name
        return data
    obj=lambda n:json.loads(read(n))
    cert_raw=read('repair67-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json');cert=json.loads(cert_raw)
    assert sha(cert_raw)=='3cb037399462d45683c9790793ed1bfbff2df2934898f38f9ffe2cd857ff4d39'
    append_raw=read('repair67-universal-20261016/RECEIPT.json');append=json.loads(append_raw)
    assert sha(append_raw)==cert['append_receipt_sha256']=='e1f764b48cfb7236c621265b7ec03b4f983523e87585dd4bf00ff6f63be28d55'
    preceding_raw=read('repair53-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json');preceding=json.loads(preceding_raw)
    assert sha(preceding_raw)==cert['preceding53_certificate_sha256']=='02142a036ecbd985b4885f971a0f0027bd3df034fda42a82e44b37e67a1f9593'
    trusted=json.loads((root.parent/'product67-native-20261016/universal67/CACHE_EQUIVALENCE_CERTIFICATE.json').read_text())
    for key in ['source_files_sha256','protected_dependency_files_sha256','verifier_executable_sha256']:
        assert cert[key]==preceding[key]==trusted[key]
    assert cert['no_sampled_inputs'] and append['no_simulated_inputs']
    assert not cert['original4b_coordinate_function_transfer'] and not cert['global_A29_MR_independence_proved']
    freeze_raw=read('REPAIR67_FREEZE.json');freeze=json.loads(freeze_raw)
    assert sha(freeze_raw)==cert['source_freeze_sha256']
    assert freeze['stages'][:53]==obj('REPAIR53_FREEZE.json')['stages']
    assert sha(read('repair67-native-20261016/NATIVE_RECEIPT.json'))==cert['native_receipt_sha256']
    assert len(append['stages'])==14
    previous=preceding['candidate_stream_sha256'];leases=uses=0
    for i,row in enumerate(append['stages'],54):
        assert row['stage']==i and row['status']=='PASS' and row['returncode']==0
        assert row['config']==freeze['stages'][i-1] and row['input_sha256']==previous
        raw=read(row['audit_log']);assert sha(raw)==row['audit_log_sha256'];log=raw.decode()
        if row['lease_log']=='=':assert row['input_sha256']==row['output_sha256'] and 'UNIVERSAL_BYTE_IDENTITY_PASS' in log
        else:
            assert sha(read(row['lease_log']))==row['lease_log_sha256']
            assert 'UNIVERSAL_CACHE_CERTIFICATE_PASS' in log and 'independent_zero_and_product_passes=true' in log
            leases+=int(re.search(r'leases=(\d+)',log).group(1));uses+=int(re.search(r'uses=(\d+)',log).group(1))
        previous=row['output_sha256']
    assert previous==cert['candidate_stream_sha256']==freeze['external_stream_sha256']=='0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b'
    assert leases==cert['append_leases_verified']==43131 and uses==cert['append_replaced_uses_verified']==106818
    assert leases+preceding['leases_verified']==cert['leases_verified']==245849
    assert uses+preceding['replaced_uses_verified']==cert['replaced_uses_verified']==540826
    transfer_raw=read('repair67-universal-20261016/PER_INPUT_MASK_TRANSFER.json');transfer=json.loads(transfer_raw)
    assert sha(transfer_raw)=='0bfcc1dd3657e1c8eb6ae8ce404c1c91da22eb9c7b3622d3ad8dbfecbf12a1e3'
    assert transfer['certificate_sha256']==sha(cert_raw) and transfer['candidate_stream_sha256']==previous
    assert transfer['baseline_A29_stream_sha256']==cert['baseline_stream_sha256']=='1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522'
out=dict(status='INDEPENDENT_ALL14_ACTUAL_APPEND_LOGS_AND_FULL67_SOURCE_CHAIN_PASS',archive_sha256=sha(next_path.read_bytes()),append_stages=14,total_stages=67,append_leases=leases,append_uses=uses,total_leases=245849,total_uses=540826,identical_reviewed_kernel_and_protected_dependencies=True,original4b_mask_transfer_requires_separate_conditional_theorem=True,no_nonce_or_benchmark_record=True)
(root/'repair67-universal-20261016/ROOT_APPEND_LOG_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
