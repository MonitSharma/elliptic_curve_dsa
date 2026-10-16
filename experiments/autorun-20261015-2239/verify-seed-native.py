from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
base=Path(__file__).resolve().parents[2]/'experiments';root=base/'seed-restore-20261016';p=root/'native-source-freeze-v1.tar.gz'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='7b1b9452aade402546069fa2143b389edcd13d7f940a92f1384852437446b582'
with tarfile.open(p) as t:
 names=t.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 assert all(m.isfile() or m.isdir() for m in t.getmembers());prefix='native-source-freeze-v1/';read=lambda n:t.extractfile(prefix+n).read()
 manifest=json.loads(read('MANIFEST.json'));assert len(manifest['files'])==207
 for n,v in manifest['files'].items():
  raw=read(n);assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'],n
 assert manifest['diagnosis_archive_sha256']==hashlib.sha256((base/'current-value-attribution-20261016/seed-diagnosis-v1.tar.gz').read_bytes()).hexdigest()
 sources=json.loads(read('source-files.json'));assert all(n.startswith('src/point_add/') for n in sources)
 for n,sha in sources.items():assert hashlib.sha256(read('candidate/'+n)).hexdigest()==sha,n
 declaration=read('PREDECLARATION.json');assert hashlib.sha256(declaration).hexdigest()=='98ccedaa3eaed8efa99458d2daa84aa7968d3e19ee765855aa47d606c30115c6'
 d=json.loads(declaration);assert d['all_matching_edits']==1 and d['no_witness_selected_subset']
 assert d['fresh_gate']['label']=='public4b-all-seed-dropped-control-restore-independent-20261016-v1' and d['fresh_gate']['batches']==32768
 for n in ['guard-tests.exit','native.exit','native-verification.exit','protected.exit']:assert read(n).strip()==b'0',n
 native=json.loads(read('native-verification.json'));stream=json.loads((root/'ROOT_STREAM_REVIEW.json').read_text())
 assert native['source_stream_sha256']==stream['source_sha256'] and native['canonical_sha256']==stream['canonical_sha256']
 assert stream['changed_op']==619000 and stream['all_other_11630715_ops_byte_identical'] and stream['changed_op_unconditional']
 out=dict(status='INDEPENDENT_COMPLETE_NATIVE_SOURCE_FREEZE_AND_FULL_STREAM_AUDIT_PASS',archive_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),artifacts=207,complete_point_add_files=len(sources),source_stream_sha256=stream['source_sha256'],every_other_operation_byte_identical=True,exact_added_T=1,added_Q=0,added_MR=0,full_protected_and_native_exits_pass=True,fresh_gate_pending=True,no_global_failure_or_resource_record_claim=True)
(root/'ROOT_NATIVE_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
