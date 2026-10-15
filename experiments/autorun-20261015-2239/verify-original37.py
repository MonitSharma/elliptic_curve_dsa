from pathlib import Path
import hashlib,json,struct,tarfile
root=Path(__file__).resolve().parent.parent/'original37-mask-20261016'
sha=lambda x:hashlib.sha256(x).hexdigest()
raw=(root/'evidence.tar.gz').read_bytes();assert sha(raw)=='ef7d4264ed4bb047b87ae9ce7aa9c84579ef127c2b94dbacabed26ea5c04bbbb'
with tarfile.open(root/'evidence.tar.gz') as archive:
    get=lambda name:archive.extractfile(name).read()
    report=json.loads(get('global.json'));result=json.loads(get('RESULT.json'))
    assert get('run.exit').strip()==b'0' and b'33 passed; 0 failed' in get('tests.log')
    assert get('input-before.sha256')==get('input-after.sha256')
    assert get('input-before.sha256').startswith(b'2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ')
    family=json.loads(get('a29-fold-family-v1/hints.json'))['hints'];six=json.loads(get('a29-edited-folds-v1/original-candidates.json'))
    wanted={(r['old_start'],r['old_end_exclusive']) for r in family}|set(map(tuple,six['candidate_shadow_regions']))
    accepted={(r['start'],r['end_exclusive']) for r in report['applied_shadow_contracts']}
    assert len(wanted)==37 and wanted<=accepted
    for name,h in result['generic_kernels_identical_to_frozen_original'].items():
        data=get('tool/src/'+name);assert sha(data)==h
        assert data==(root.parent/'prefilter-20261015/tool/src'/name).read_bytes()
    mask=get('evidence/mr-mask-original37.bin');assert mask[:8]==b'MRMASK01'
    assert struct.unpack_from('<QQQ',mask,8)==(2,1024,512) and len(mask)==2112
    assert struct.unpack_from('<IIIIIIII',mask,32)==(0,0,0,0,1,0,0,0)
    assert struct.unpack_from('<512I',mask,64)==(1,)*512
    assert sha(mask)=='fb1762663ca850bfd0995c55dc65bccf0a032e978e75263df2fd5bf542f61ea3'
    metadata=json.loads(get('evidence/mr-mask-original37.json'))
    assert metadata['original_stream_sha256']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
    assert metadata['dependency_roots']==[1]*512 and metadata['input_count']==1024
    assert not any(get('evidence/mr-mask-original37.audit-known-u64le.bin'))
    assert report['protected_full_state_containment_seeds']==4 and report['rng_draws']==906156
out={'status':'INDEPENDENT_TERMINAL_SOURCE_KERNEL_WHOLEFOLD_AND_ALL_ROOTS_NEGATIVE_VERIFIED',
    'archive_sha256':sha(raw),'native_tests':33,'protected_containment_streams':4,'all_requested37_folds_individually_accepted':True,
    'binary_nodes':2,'binary_roots':512,'every_dependency_root_constant_one':True,'known_output_bits':0,
    'generic_engines_equal_original':True,'active_mask_or_search_changed':False,'not_a_record_or_screening_authority':True}
(root/'ROOT_VERIFIED.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
