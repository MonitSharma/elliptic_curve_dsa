"""Review terminal disabled repaired67 rows, controls, bindings and source delta."""
from pathlib import Path,PurePosixPath
import hashlib,json,re,tarfile
root=Path(__file__).resolve().parents[2]/'experiments'
current=root/'repair67-conditional-filter-20261016'
with tarfile.open(current/'evidence.tar.gz') as archive,tarfile.open(root/'product67-filter-20261016/evidence.tar.gz') as old:
    names=archive.getnames();assert len(names)==len(set(names))
    assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
    assert all(m.isfile() or m.isdir() for m in archive.getmembers())
    read=lambda n:archive.extractfile(n).read()
    manifest=json.loads(read('manifest.json'))
    for n,h in manifest.items():assert hashlib.sha256(read(n)).hexdigest()==h,n
    assert len(manifest)==85
    assert read('run.exit').strip()==b'127' and read('run-v2.exit').strip()==b'0'
    assert read('binary-before-v2.sha256')==read('binary-after-v2.sha256')
    prepared=json.loads(read('PREPARED_SOURCE.json'))
    for n,h in prepared.items():assert hashlib.sha256(read(n)).hexdigest()==h,n
    assert json.loads(read('SOURCE_UNCHANGED.json'))['proof_accepted'] is False
    def rows(stem,count,first):
        r=sorted(map(json.loads,read(stem+'.jsonl').splitlines()),key=lambda v:v['nonce'])
        assert len(r)==count and [v['nonce'] for v in r]==list(range(first,first+count))
        assert all(v['authoritative_rejection'] is False and v['proof_accepted'] is False for v in r)
        assert b'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS nonces=1,2,17,255' in read(stem+'.err')
        return r
    for stem,count,first in [('forced2',2,1),('shadow128',128,1),('partial',11,17)]:
        assert rows(stem+'-generic',count,first)==rows(stem+'-threaded',count,first)
    for stem in ['forced2-generic','forced2-threaded']:
        err=read(stem+'.err')
        for s in [b'nonce=1 kind=phase shots=576',b'nonce=2 kind=classical shots=448']:
            assert b'FORCED_SCHEDULER_PROTECTED_KIND_PASS '+s in err
    err=read('shadow128-generic.err')
    assert b'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS nonce=1' in err
    assert b'FIXED445_GUARD_CONDITIONAL_KNOWN_BITS_PASS safe_old428 excluded_old3 excluded_repair14 checked_bits=4367' in err
    assert b'repaired_high_classical_tests::repaired_ids_roundtrip_protected_phase_and_MR ... ok' in read('wide-classical-tests-v2.log')
    reference=rows('baseline-0',4096,1)
    for stem in ['baseline-1','baseline-2','threaded-0','threaded-1','threaded-2']:assert rows(stem,4096,1)==reference
    source_names={n for n in names if n.startswith('tool/src/')}
    old_names={n for n in old.getnames() if n.startswith('tool/src/')}
    assert source_names==old_names|{'tool/src/guard.rs'}
    changed={n for n in old_names if read(n)!=old.extractfile(n).read()}
    assert changed=={'tool/src/packed_body.rs','tool/src/transfer.rs','tool/src/fast_sim_wide.rs'}
    oldwide=old.extractfile('tool/src/fast_sim_wide.rs').read().decode().replace('\r\n','\n')
    assert read('tool/src/fast_sim_wide.rs').decode().startswith(oldwide)
    packed=read('tool/src/packed_body.rs').decode()
    assert 'const PROOF_ACCEPTED:bool=false;' in packed and 'Some(original.as_ref().unwrap().as_slice())' in packed
    assert 'assert_eq!((nq,nb),(1234,66245))' in packed and 'guard_safe(&proposed)' in packed
    binding=read('COMPOSITE_BINDING.json');assert hashlib.sha256(binding).hexdigest()=='d19c011287293671ae14a87b380c5fbf17a9ac0009d8dd27c5966c3830525909'
    assert hashlib.sha256(binding).hexdigest() in read('tool/src/transfer.rs').decode()
    assert json.loads(binding)['conditional_theorem_sha256']=='b351ae4cbf4fab52a8248a83d517502c331a0a4291f73f0123370cad645a2c03'
    actual=json.loads(read('actual-runtime-bindings-20261015-230002.json'))
    assert actual['rows'][0]['selected_nonsecret_environment']['SCALAR_FAST_LIB']==''
    assert actual['rows'][0]['scalar_binding_verified']
    result=json.loads(read('RESULT.json'))
    assert result['status']=='DISABLED_REPAIRED67_CONDITIONAL_PIPELINE_QUALIFICATION_PASS'
    assert result['median_seconds']=={'baseline':28.89771,'threaded':28.69197}
out=dict(status='INDEPENDENT_TERMINAL_DISABLED_REPAIRED67_SOURCE_ROWS_CONTROLS_AND_BINDINGS_PASS',archive_sha256=hashlib.sha256((current/'evidence.tar.gz').read_bytes()).hexdigest(),artifacts=85,full4096_trials=6,all_rows_identical=True,full9024_q_b_phase_MR=True,known_bits_checked_on_fixed445=4367,retained_witnesses=418,forced_protected_phase_and_classical_scheduler_controls=True,classical_high_ids=[65535,66244],source_delta_only_candidate_proof_guard_and_test=True,actual_scalar_library_verified=True,no_runtime_search_authority_or_nonce_selected=True,no8_or48thread_forecast=True)
(current/'ROOT_RUNTIME_VERIFIED.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
