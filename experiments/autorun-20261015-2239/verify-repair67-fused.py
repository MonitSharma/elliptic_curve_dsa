"""Check frozen representation-only runtime delta and every qualification row."""
from pathlib import Path,PurePosixPath
import hashlib,json,statistics,tarfile
root=Path(__file__).resolve().parents[2]/'experiments'
folder=root/'repair67-fused-filter-20261016'
p=folder/'evidence.tar.gz'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='7af8c67adb7698f01a43af981b8f1a6c78930d1178dc65ac5fbc69bbcf2de85b'
with tarfile.open(p) as t,tarfile.open(root/'repair67-conditional-filter-20261016/evidence.tar.gz') as old:
 names=t.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 assert all(m.isfile() or m.isdir() for m in t.getmembers())
 read=lambda n:t.extractfile(n).read()
 m=json.loads(read('MANIFEST.json'));assert len(m['files'])==79
 for item in m['files']:
  raw=read(item['path']);assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],item['path']
 assert read('run.exit').strip()==b'0' and read('binary-before.sha256')==read('binary-after.sha256')
 prepared=json.loads(read('PREPARED_SOURCE.json'));assert len(prepared)==16
 for n,sha in prepared.items():assert hashlib.sha256(read(n)).hexdigest()==sha
 oldnames={n for n in old.getnames() if n.startswith('tool/') and n.endswith(('.rs','.toml','.lock'))}
 assert set(prepared)==oldnames|{'tool/src/fused_guard.rs'}
 changed={n for n in oldnames if read(n)!=old.extractfile(n).read()}
 assert changed=={'tool/src/fast_curve_c.rs','tool/src/guard.rs','tool/src/packed_body.rs'}
 oldguard=old.extractfile('tool/src/guard.rs').read().decode()
 assert read('tool/src/guard.rs').decode()=='include!("fused_guard.rs");\n'+oldguard.replace('fn guard_safe(', 'fn guard_safe_raw(')
 packed=old.extractfile('tool/src/packed_body.rs').read().decode()
 assert read('tool/src/packed_body.rs').decode()==packed.replace('if std::env::var_os("FIXED_TRANSFER_SHADOW").is_some(){validate_fixed_transfer(', 'if std::env::var_os("FIXED_TRANSFER_SHADOW").is_some(){validate_guard_components();validate_fixed_transfer(')
 assert 'const PROOF_ACCEPTED:bool=false;' in packed
 oldcurve=old.extractfile('tool/src/fast_curve_c.rs').read().decode()
 pin='sha_check(&path,"3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f");'
 assert read('tool/src/fast_curve_c.rs').decode()==oldcurve.replace('let path=CString::new(path).unwrap();',pin+'let path=CString::new(path).unwrap();')
 def rows(archive,n,count,first):
  rs=sorted(map(json.loads,archive.extractfile(n+'.jsonl').read().splitlines()),key=lambda v:v['nonce'])
  assert len(rs)==count and [r['nonce'] for r in rs]==list(range(first,first+count))
  assert all(r['authoritative_rejection'] is False and r['proof_accepted'] is False for r in rs)
  assert b'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS' in archive.extractfile(n+'.err').read()
  return rs
 reference=rows(old,'baseline-0',4096,1)
 for mode in ['raw','fused']:
  for trial in range(3):assert rows(t,f'{mode}-{trial}',4096,1)==reference
  for stem,prior,count,first in [('forced2','forced2-generic',2,1),('shadow128','shadow128-generic',128,1),('partial11','partial-generic',11,17)]:
   assert rows(t,stem+'-'+mode,count,first)==rows(old,prior,count,first)
  err=read('shadow128-'+mode+'.err')
  for marker in [b'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS',b'FIXED445_GUARD_CONDITIONAL_KNOWN_BITS_PASS',b'FUSED_GUARD_FIXED445_AUDIT32_PARTIAL_POLARITY_PASS']:assert marker in err
  forced=read('forced2-'+mode+'.err')
  for marker in [b'nonce=1 kind=phase shots=576',b'nonce=2 kind=classical shots=448']:assert marker in forced
 result=json.loads(read('RESULT.json'));assert result['proof_accepted'] is False and result['nonce_selected'] is None
 for mode in ['raw','fused']:assert statistics.median(result['times_seconds'][mode])==result['median_seconds'][mode]
 receipt=json.loads(read('TERMINAL-EVIDENCE-RECEIPT.json'))
 assert receipt['binary_sha256']=='ab8cf13ceca99f8418ba490e7e02be7b0611a55de975a3451c5943d55c25e28b'
 assert receipt['runtime_artifacts']['/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so']=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
 reconstruction=json.loads((root/'guard-fused-20261016/ROOT_FUNCTION_RECONSTRUCTION.json').read_text())
 assert reconstruction
out=dict(status='INDEPENDENT_DISABLED_FUSED_RUNTIME_SOURCE_ALL_ROWS_AND_CONTROLS_PASS',archive_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),artifacts=79,source_files=16,all_six_4096_rows_equal_precursor=True,full9024_q_b_phase_MR_and_wide_id_controls=True,sole_source_changes='new equivalent G evaluator, raw rename/include, control-only hook and resolved scalar pin',binary_sha256=receipt['binary_sha256'],no_search_authority=True,no8thread_forecast=True)
(folder/'ROOT_RUNTIME_VERIFIED.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
