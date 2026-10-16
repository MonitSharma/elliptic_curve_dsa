"""Review frozen ALL70 native source and existing-witness all-add attribution."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
ROOT=Path(__file__).resolve().parents[2]/'experiments'
sha=lambda b:hashlib.sha256(b).hexdigest()
cases=[('product-exact-20261015','all70-base-native-evidence.tar.gz','manifest.json','0c9afdc441dd7801524aea236f3d46f2c84b9eae2e92d4e004ea1cb1dad79258'),
       ('current-value-attribution-20261016','all-add-attribution-addendum-v3.tar.gz','all-add-attribution-addendum-v3/MANIFEST.json','a7b7612d9b6ed25ada46c01c81130460dd3b8bb1e3c64a156583aa2778232f22')]
for folder,archive,m,expected in cases:
    path=ROOT/folder/archive;assert sha(path.read_bytes())==expected
    with tarfile.open(path) as t:
        names=t.getnames();assert len(names)==len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert all(v.isfile() or v.isdir() for v in t.getmembers())
        read=lambda n:t.extractfile(n).read()
        load=lambda n:json.loads(read(n))
        manifest=load(m);prefix=m[:-len(PurePosixPath(m).name)]
        for name,record in manifest['files'].items():
            data=read(prefix+name);assert len(data)==record['bytes'] and sha(data)==record['sha256'],name
        if archive.startswith('all70'):
            base='all70-cache67-20261016/';r=load(base+'BASE_NATIVE_RECEIPT.json')
            for name,digest in r['source_files_sha256'].items():assert sha(read(base+'base-point-add-source/'+name))==digest,name
            for name,digest in r['protected_files_sha256'].items():assert sha(read(base+'base-protected-inputs/'+name))==digest,name
            assert len(r['protected_files_sha256'])==17
            assert r['diff_paths']==['src/point_add/census_cut.rs']
            assert r['ops']==11630716 and r['restored']==70
            assert r['untouched_other_records'] and r['MR_classical_order_and_physical_positions_unchanged'] and r['all74_deletions_retained']
            assert read(base+'base-launcher.exit').strip()==b'0'
            assert r['source_sha256']=='06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a'
            detail=dict(full_source_files=len(r['source_files_sha256']),protected_files=17,only_point_add_census_cut_changed=True,
                        native_receipt_only_base_no_cache_or_census_claim=True)
            output='ROOT_ALL70_BASE_REVIEW.json'
        else:
            r=load(prefix+'ALL-ADD-ATTRIBUTION.json');join=load(prefix+'all-add-first-global-join.json')
            assert r['no_new_sampling'] and r['no_candidate'] and r['source_before_after_identical']
            assert r['all_original_q_b_phase_T_and_failure_masks_reproduced']
            assert r['events']==r['shots_with_local_add_mismatch']==len(r['all_events'])==89
            assert all(e['phase']=='divide' and e['tick']=='131' and e['rev']=='false' for e in r['all_events'])
            assert len({e['shot'] for e in r['all_events']})==89
            assert r['remaining_shot38243_local_add_events']==[]
            assert sha(read(prefix+'all-add-replay.log'))==r['log_sha256']
            assert join['all89_add_errors']==89 and join['not_an_end_to_end_repair_count']
            assert join['by_first_global_stage']=={'divide':89}
            assert read(prefix+'all-add-replay.exit').strip()==b'0'
            detail=dict(existing_witnesses_only=True,local_add_errors=89,all_at_divide_forward131=True,no_end_to_end_repair_claim=True)
            output='ROOT_ALL_ADD_V3_REVIEW.json'
    result=dict(status='ROOT_ALL_FROZEN_MEMBER_HASHES_SOURCE_AND_RESULT_CONSISTENCY_PASS',archive_sha256=expected,stored_files=len(manifest['files']),detail=detail)
    (ROOT/folder/output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
