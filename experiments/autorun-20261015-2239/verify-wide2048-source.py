from pathlib import Path,PurePosixPath
import hashlib,io,json,tarfile
base=Path(__file__).resolve().parents[2]/'experiments';root=base/'wide2048-native-20261016'
with tarfile.open(root/'evidence.tar.gz') as archive:
    result=json.load(archive.extractfile('wide2048/RESULT.json'))
    assert not result['nonce_eligible'] and not result['nonce_search'] and not result['resource_record']
    assert result['stream_sha256']=='f84c499f7c085847355cd8d5db8154fce8f66d7da99a1f99f871d2125232ebfb'
    assert result['native_tests']==4 and all(p.startswith('src/point_add/') for p in result['changed_files'])
    manifest=json.load(archive.extractfile('wide2048/native-source.json'))
    raw=archive.extractfile('wide2048/point-add-source.tar.gz').read()
    assert hashlib.sha256(raw).hexdigest()==result['full_source_archive_sha256']
    with tarfile.open(fileobj=io.BytesIO(raw)) as source:
        names=source.getnames();assert len(names)==len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert all(m.isfile() or m.isdir() for m in source.getmembers())
        assert {m.name for m in source.getmembers() if m.isfile()}==set(manifest)
        for name,sha in manifest.items():assert hashlib.sha256(source.extractfile(name).read()).hexdigest()==sha,name
    dependency=json.loads((base/'product67-native-20261016/universal67/CACHE_EQUIVALENCE_CERTIFICATE.json').read_text())['protected_dependency_files_sha256']
    protected=json.load(archive.extractfile('wide2048/protected.json'))
    for name,sha in dependency.items():assert protected[name]==sha,name
    summary=json.load(archive.extractfile('wide2048/census-summary.json'))
    reference=json.load(archive.extractfile('wide2048/reference753721-comparison.json'))
    assert summary['failed_batches']=={'parent':1338,'candidate':1351} and reference['reference_failed_batches']==1350
    for role,expected in [('parent',1338),('candidate',1351),('reference753721',1350)]:
        rows=list(map(json.loads,archive.extractfile(f'wide2048/{role}-census.jsonl').read().splitlines()))
        assert len(rows)==32768 and sorted(r['batch'] for r in rows)==list(range(32768))
        assert all(r['shots']==64 and r['skipped']==0 and r['dirty_shots']==0 for r in rows)
        assert sum(bool(r['failures']) for r in rows)==expected
report={'status':'INDEPENDENT_FULL_SOURCE_PROTECTED_DEPENDENCIES_AND_ALL_THREE_FIXED_COHORTS_VERIFIED','full_source_files':len(manifest),'full_source_archive_sha256':result['full_source_archive_sha256'],'point_add_only_changed_paths':result['changed_files'],'protected_dependencies_verified':len(dependency),'batches_per_source':32768,'failed_batches':{'original5a':1338,'candidate':1351,'official753721':1350},'failed_gate_no_nonce_authorized':True,'not_a_resource_record':True}
(root/'ROOT_SOURCE_AND_CENSUS_VERIFIED.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
