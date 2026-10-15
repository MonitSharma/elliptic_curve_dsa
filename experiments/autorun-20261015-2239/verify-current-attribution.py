"""Independent archive, protected source, all-context and14-cause receipt audit."""
from pathlib import Path,PurePosixPath
import collections,hashlib,json,re,tarfile
root=Path(__file__).resolve().parents[2]/'experiments/current-value-attribution-20261016'
path=root/'attribution-checkpoint-v1.tar.gz';digest=hashlib.sha256(path.read_bytes()).hexdigest()
assert digest=='ff142400c88f8b6f33aff4afdee6f5621378292a2c75c9e90415813eca337382'
prefix='attribution-checkpoint-v1/'
with tarfile.open(path) as archive:
    names=archive.getnames();assert len(names)==len(set(names))
    assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
    assert all(m.isfile() or m.isdir() for m in archive.getmembers())
    read=lambda name:archive.extractfile(prefix+name).read()
    manifest=json.loads(read('MANIFEST.json'))
    for name,info in manifest['files'].items():
        data=read(name);assert len(data)==info['bytes'] and hashlib.sha256(data).hexdigest()==info['sha256'],name
    assert len(manifest['files'])==326 and len(manifest['external'])==4
    trusted=json.loads((root.parent/'product-exact-20261015/repair67-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json').read_text())['protected_dependency_files_sha256']
    for name in ['Cargo.toml','Cargo.lock','src/sim.rs','src/circuit.rs','src/lib.rs','src/weierstrass_elliptic_curve.rs','src/bin/build_circuit.rs','src/bin/eval_circuit.rs']:
        assert hashlib.sha256(read('protected-reference/'+name)).hexdigest()==trusted[name],name
    for name in ['actual-replay.exit','add-replay.exit','dirty-add-replay.exit','dirty-low-protected.exit']:
        assert read(name).strip()==b'0',name
    log=read('actual-replay.log').decode();summary=json.loads(read('attribution-summary.log'))
    census=list(map(json.loads,read('packets/expected-census.jsonl').splitlines()))
    assert len(census)==413 and len({r['batch'] for r in census})==413
    batch_rows=re.findall(r'^ATTR_BATCH batch=(\d+) tracked=(\d+) full64q_b_phase_T_equal=true original_census_flags_reproduced=true$',log,re.M)
    assert len(batch_rows)==413 and {int(b) for b,_ in batch_rows}=={r['batch'] for r in census}
    shots=re.findall(r'^PAY_SHOT family=tip431 shot=(\d+) final_bad=true event=(?:true|false) observer_equal=true$',log,re.M)
    expected={r['batch']*64+f['lane'] for r in census for f in r['failures'] if f['value']}
    assert len(shots)==len(set(shots))==len(expected)==431 and set(map(int,shots))==expected
    assert sum(int(n) for _,n in batch_rows)==431
    assert summary['target_witnesses']==431 and summary['context_shots']==413*64==26432
    assert summary['event_counts']['FOLD_LOW_MISMATCH']==0 and 'FOLD_LOW_MISMATCH family=' not in log
    assert summary['marker_coverage']['unknown_regions']==3
    unseen=summary['advisory_model_unexplained'];assert unseen['shots']==55 and unseen['batches']==54
    assert unseen['lambda_value_affected_batches_per9024']==54/4096*141==1.85888671875
    diagnosis=json.loads(read('N2-DIAGNOSIS.json'));cases=diagnosis['cases']
    assert len(cases)==14 and len({c['shot'] for c in cases})==14
    assert all(c['shot']==c['batch']*64+c['lane'] and c['shot'] in expected for c in cases)
    rails=collections.Counter()
    for c in cases:
        rail=abs(c['parked_signed6bit_rails'][1]);rails[rail]+=1
        q,bit=(555,2) if rail==5 else (556,3)
        assert rail in [3,5] and c['dirty_q']==q and c['injected_carry_bit']==bit
        assert abs(c['exact_sum_error'])==1<<bit
    assert rails=={5:8,3:6}
    source=read('tool/src/payload_runtime.rs').decode()
    for required in ['assert_eq!(U256::from_le_bytes(rb),wanted','assert_eq!(sim.qubits,reference.qubits)','assert_eq!(sim.bits,reference.bits)','assert_eq!(sim.phase,reference.phase)','assert_eq!(sim.stats.toffoli_gates,reference.stats.toffoli_gates)','assert_eq!([value_mask,sim.phase,dirty],desired','assert_eq!(sim.stats.toffoli_gates,expected_batch["toffoli"]']:
        assert required in source,required
    family=json.loads(read('n2-loan-family.json'))
    assert family['source_call_sites']==2 and family['source_rail_loans']==4 and family['source_loan_release_clean_calls']==16
out=dict(status='INDEPENDENT_ARCHIVE_PROTECTED_SOURCE_ALL413_CONTEXTS_431_WITNESSES_AND14_N2_DIAGNOSIS_REVIEW_PASS',archive_sha256=digest,archive_members_verified=326,protected_files_checked=8,full_contexts=413,shots=26432,value_witnesses=431,N2_cases=14,parked_abs5_cases=8,parked_abs3_cases=6,source_runtime_assertions_reviewed=True,external_stream_hashrefs=4,external_streams_not_claimed_archived_or_locally_rehashed=True,no_fresh_census_or_repair_or_record=True)
(root/'ROOT_ATTRIBUTION_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
