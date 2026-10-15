"""Independent source, universal-prefix and full raw-lane review of one checkpoint."""
from pathlib import Path,PurePosixPath
import gzip,hashlib,io,json,re,tarfile
root=Path(__file__).resolve().parents[2]/'experiments/product-exact-20261015'
sha=lambda data:hashlib.sha256(data).hexdigest()
delta_path=root/'supplement-repaired67-qualified-20261016.tar.gz'
assert sha(delta_path.read_bytes())=='9ec9889206393fd00ee7188c969c5fcdeffe6b23e34673acb9ba93dec047561e'
with tarfile.open(root/'evidence.tar.gz') as base,tarfile.open(delta_path) as delta:
    for archive in [base,delta]:
        names=archive.getnames();assert len(names)==len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert all(m.isfile() or m.isdir() for m in archive.getmembers())
    manifest=json.load(delta.extractfile('increment/manifest.json'))
    receipt=json.load(delta.extractfile('increment/current-receipt.json'))
    stored=set(manifest['stored_new_or_changed_paths'])
    def read(name):
        if name not in receipt['files'] and name+'.gz' in receipt['files']:
            return gzip.decompress(read(name+'.gz'))
        if name in stored:data=delta.extractfile('increment/artifacts/'+name).read()
        elif name in manifest.get('exact_gzip_mtime_byte_patches',{}):
            patch=manifest['exact_gzip_mtime_byte_patches'][name]
            data=base.extractfile('evidence/'+patch['base_path']).read()
            data=data[:4]+bytes.fromhex(patch['mtime_bytes_hex'])+data[8:]
        else:data=base.extractfile('evidence/'+manifest['copy_from_base_artifact_path'].get(name,name)).read()
        assert sha(data)==receipt['files'][name],name
        return data
    obj=lambda name:json.loads(read(name))
    cert_raw=read('repair53-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json')
    assert sha(cert_raw)=='02142a036ecbd985b4885f971a0f0027bd3df034fda42a82e44b37e67a1f9593'
    cert=json.loads(cert_raw);chain_raw=read('repair53-universal-20261016/RECEIPT.json');chain=json.loads(chain_raw)
    assert sha(chain_raw)==cert['receipt_sha256'] and len(chain['stages'])==53
    assert cert['stage_count']==53 and cert['no_sampled_inputs']
    assert not cert['original4b_coordinate_function_transfer'] and not cert['global_A29_MR_independence_proved']
    trusted=json.loads((root.parent/'product67-native-20261016/universal67/CACHE_EQUIVALENCE_CERTIFICATE.json').read_text())
    assert cert['verifier_executable_sha256']==trusted['verifier_executable_sha256']
    assert cert['source_files_sha256']==trusted['source_files_sha256']
    assert cert['protected_dependency_files_sha256']==trusted['protected_dependency_files_sha256']
    assert sha(read('REPAIR53_FREEZE.json'))==cert['source_freeze_sha256']
    assert sha(read('repair53-native-20261016/NATIVE_RECEIPT.json'))==cert['native_receipt_sha256']
    previous=cert['baseline_stream_sha256'];assert previous=='1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522'
    leases=uses=0
    for i,row in enumerate(chain['stages'],1):
        assert row['stage']==i and row['status']=='PASS' and row['returncode']==0
        assert row['input_sha256']==previous
        log_raw=read(row['audit_log']);assert sha(log_raw)==row['audit_log_sha256'];log=log_raw.decode()
        if row['lease_log']=='=':
            assert row['input_sha256']==row['output_sha256'] and 'UNIVERSAL_BYTE_IDENTITY_PASS' in log
        else:
            assert sha(read(row['lease_log']))==row['lease_log_sha256']
            assert 'UNIVERSAL_CACHE_CERTIFICATE_PASS' in log and 'independent_zero_and_product_passes=true' in log
            leases+=int(re.search(r'leases=(\d+)',log).group(1));uses+=int(re.search(r'uses=(\d+)',log).group(1))
        previous=row['output_sha256']
    assert previous==cert['candidate_stream_sha256']=='13d1f7341415847c50e94de8fd835ee24ed7b7acc44d9adf66e59afe727abaae'
    assert leases==cert['leases_verified']==202718 and uses==cert['replaced_uses_verified']==434008
    transfer=obj('repair53-universal-20261016/PER_INPUT_MASK_TRANSFER.json')
    assert transfer['certificate_sha256']==sha(cert_raw) and transfer['baseline_A29_stream_sha256']==cert['baseline_stream_sha256']
    native_raw=read('repair67-native-20261016/NATIVE_RECEIPT.json');native=json.loads(native_raw)
    assert sha(native_raw)=='5510d21cf7e862e78c9af486b7b7644696be4d1d4f1c95f9f0418f4ad737932d'
    assert native['native_stream_sha256']=='0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b'
    assert native['native_loader_tests']==9 and native['native_precision_tests']==9
    assert native['protected_files_sha256']==trusted['protected_dependency_files_sha256']
    assert all(p.startswith('src/point_add/') and '..' not in PurePosixPath(p).parts for p in native['diff_paths'])
    source_raw=read('repair67-native-20261016/point-add-source.tar.gz')
    assert sha(source_raw)=='25ef5a091c363ba8ba4abca779a6d3f0131335e7bc89da12d0cbf0eac326da05'
    with tarfile.open(fileobj=io.BytesIO(source_raw)) as source:
        names=source.getnames();assert len(names)==len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert {m.name for m in source.getmembers() if m.isfile()}=={'point_add/'+p for p in native['source_files_sha256']}
        for name,h in native['source_files_sha256'].items():assert sha(source.extractfile('point_add/'+name).read())==h,name
    failure_report=obj('repair67-native-20261016/PER_SHOT_FAILURE_COMPARISON.json')
    rows=[]
    for role in ['parent','candidate']:
        raw=gzip.decompress(read(f'repair67-native-20261016/{role}-census.jsonl.gz'))
        assert sha(raw)==failure_report[f'{role}_rows_sha256']
        data=list(map(json.loads,raw.splitlines()))
        assert len(data)==32768 and [r['batch'] for r in data]==list(range(32768))
        assert all(r['shots']==64 and not r['skipped'] for r in data)
        for row in data:
            assert len({f['lane'] for f in row['failures']})==len(row['failures'])
            assert all(0<=f['lane']<64 for f in row['failures'])
            for category in ['value','phase','dirty']:assert sum(bool(f[category]) for f in row['failures'])==row[category+'_shots']
        rows.append(data)
    categories={}
    for category in ['all','value','phase','dirty']:
        p,c=[{(r['batch'],f['lane']):(f['k1'],f['k2']) for r in data for f in r['failures'] if category=='all' or f[category]} for data in rows]
        assert all(p[k]==c[k] for k in p.keys()&c.keys())
        values=dict(parent_failed_shots=len(p),candidate_failed_shots=len(c),parent_only_failed_shots=len(p.keys()-c.keys()),candidate_only_failed_shots=len(c.keys()-p.keys()),same_failure_lanes=len(p.keys()&c.keys()))
        assert values==failure_report['categories'][category];categories[category]=values
    assert categories['value']['parent_only_failed_shots']==12 and categories['value']['candidate_only_failed_shots']==0
    summary=obj('repair67-census-summary.json');assert summary['failed_batches']=={'parent':4138,'candidate':4134} and summary['failure_gate_pass']
    assert [sum(bool(r['failures']) for r in data) for data in rows]==[4138,4134]
    assert categories['dirty']['parent_failed_shots']==categories['dirty']['candidate_failed_shots']==0
out=dict(status='INDEPENDENT_REPAIRED53_UNIVERSAL_PREFIX_AND_REPAIRED67_NATIVE_ALL_RAW_LANES_VERIFIED',
    checkpoint_sha256=sha(delta_path.read_bytes()),universal53_stages=53,leases=leases,uses=uses,
    verifier_and_source_match_previously_reviewed_kernel=True,repaired67_point_add_files=len(native['source_files_sha256']),
    repaired67_native_tests=18,shots_per_source=2097152,categories=categories,
    repaired67_final14_universal_stages_not_certified_by_this_checkpoint=True,
    no_original4b_arithmetic_mask_transfer=True,no_nonce_or_full_benchmark=True)
(root/'ROOT_REPAIRED67_CHECKPOINT_VERIFIED.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
