from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
root=Path(__file__).resolve().parent.parent
source=root/'product-exact-20261015/repair53-native-20261016'
archive=source/'point-add-source.tar.gz';expected='ae16455aa839274355e0630870f92fc1aed10a24e7a6ee55bc09212aa7aaf890'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
receipt=json.loads((source/'NATIVE_RECEIPT.json').read_text())
assert hashlib.sha256((source/'NATIVE_RECEIPT.json').read_bytes()).hexdigest()=='27d04e4a54cf2c0139c57deb52703bb8f213a83d64fa3c05df45252ba921e644'
assert receipt['native_stream_sha256']=='13d1f7341415847c50e94de8fd835ee24ed7b7acc44d9adf66e59afe727abaae'
assert receipt['native_loader_tests']==9 and receipt['native_precision_tests']==9
assert receipt['source_base_revision']=='4b2ec52fc55da796aa8f5ef851290297e8706424'
assert all(p.startswith('src/point_add/') and '..' not in PurePosixPath(p).parts for p in receipt['diff_paths'])
with tarfile.open(archive) as data:
 names=data.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 actual_files={m.name for m in data.getmembers() if m.isfile()}
 assert actual_files=={'point_add/'+p for p in receipt['source_files_sha256']}
 for p,sha in receipt['source_files_sha256'].items():assert hashlib.sha256(data.extractfile('point_add/'+p).read()).hexdigest()==sha,p
reference=json.loads((root/'product67-native-20261016/universal67/CACHE_EQUIVALENCE_CERTIFICATE.json').read_text())['protected_dependency_files_sha256']
assert receipt['protected_files_sha256']==reference
report={'status':'INDEPENDENT_COMPLETE_NATIVE_REPAIR53_SOURCE_HASH_REVIEW_PASS','point_add_files_verified':len(receipt['source_files_sha256']),'archive_sha256':expected,'all_binary_source_tables_included':True,'point_add_only_diff_paths':receipt['diff_paths'],'protected_receipt_matches_previously_pinned_harness':True,'native_stream_sha256':receipt['native_stream_sha256'],'native_tests_reported':18,'full_unchanged_benchmark_not_yet_run':True,'does_not_certify_original_mask_transfer':True}
(root/'product-exact-20261015/ROOT_REPAIR53_SOURCE_VERIFIED.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
