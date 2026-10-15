from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert (r/'run.exit').read_text().strip()=='0'
assert (r/'binary-before.sha256').read_bytes()==(r/'binary-after.sha256').read_bytes()
assert json.loads((r/'SOURCE_UNCHANGED.json').read_text())['status']=='ALL_PRIVATE_SOURCE_FILES_UNCHANGED'
for name,digest in json.loads((r/'PREPARED_SOURCE.json').read_text()).items():assert sha(r/name)==digest,name
result=json.loads((r/'RESULT.json').read_text());assert result['all4096rows_equal_prior_completed_rows']
rows=[]
for mode in ['raw','fused']:
 for trial in range(3):
  p=r/f'{mode}-{trial}.jsonl';data=sorted(map(json.loads,p.read_text().splitlines()),key=lambda x:x['nonce'])
  assert len(data)==4096 and [x['nonce']for x in data]==list(range(1,4097))
  assert all(x['proof_accepted']is False and x['authoritative_rejection']is False for x in data)
  rows.append(data)
assert all(x==rows[0]for x in rows)
runtime_paths=[
 r.parent/'product-exact-20261015/repair-to67-rank-20261016/repair-67-retained-1024-proxy.bin',
 r.parent/'prefilter-20261015/a29-conditional-certificate-v1/CONDITIONAL_TRANSFER_CERTIFICATE.json',
 r.parent/'prefilter-20261015/a29-conditional-prefix-v1/public-discrepancy-guard.bin',
 r.parent/'prefilter-20261015/evidence/mr-mask-tip-v3-fused.bin',
 r.parent/'zero-mr-slice-20261016/tip.compact16.bin',
 r.parent/'guard-fused-20261016/guard512.bin',r.parent/'guard-fused-20261016/guard-fused.bin',
 r.parent/'guard-fused-20261016/guard-fused.nodeids-u32le.bin',r.parent/'guard-fused-20261016/COMPILATION-LINEAGE.json',
 r.parent/'product-exact-20261015/repair67-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json',
 r.parent/'product-exact-20261015/repair67-universal-20261016/PER_INPUT_MASK_TRANSFER.json']
runtime_artifacts={str(p):sha(p)for p in runtime_paths}
captures=sorted(r.glob('ACTUAL_RUNTIME_BINDINGS-*.json'));assert captures,'Missing actual resolved library receipt'
for path in captures:
 for item in json.loads(path.read_text())['rows']:
  assert item['actual_scalar_library_verified']
  for name,digest in item['mapped_research_library_sha256'].items():
   assert sha(Path(name))==digest;runtime_artifacts[name]=digest
assert runtime_artifacts[str(r.parent/'scalar-fast-20261015/libscalar_fast_batch.so')]=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
receipt={'status':'COMPLETE_DISABLED_ROW_AUDIT_SOURCE_BINARY_HASHES_AND_NO_AUTHORITY_PASS',
 'prepared_source_sha256':sha(r/'PREPARED_SOURCE.json'),'diff_sha256':sha(r/'SOURCE-DIFF.patch'),
 'result_sha256':sha(r/'RESULT.json'),'all_six4096_arrays_identical':True,
 'canonical4096_rows_sha256':hashlib.sha256(('\n'.join(json.dumps(x,sort_keys=True,separators=(',',':'))for x in rows[0])+'\n').encode()).hexdigest(),
 'binary_sha256':(r/'binary-before.sha256').read_text().split()[0],
 'executable_path':str(r/'tool/target/release/value_prefilter'),
 'runtime_artifacts':runtime_artifacts,
 'fused_mode_environment':{'FUSED_GUARD':'1','FAST_ZERO_DISPATCH':'absent','SCALAR_FAST_LIB':'absent (pinned default path)','proof_accepted':False},
 'process_memory_cap_GiB':24,'qualification_threads':2,
 'measured_two_thread_medians':result['median_seconds'],
 'no_8thread_forecast_or_search_authority':True}
(r/'TERMINAL-EVIDENCE-RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
archive=r/'evidence.tar.gz';assert not archive.exists()
files=[p for p in r.rglob('*')if p.is_file()and'target'not in p.relative_to(r).parts and'__pycache__'not in p.relative_to(r).parts]
manifest={'status':'DISABLED_OPTIONAL_FUSED_GUARD_RUNTIME_ALL_SOURCE_AND_EVIDENCE',
 'files':[{'path':p.relative_to(r).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(files)],
 'hashrefs':[
 {'path':'../repair67-conditional-filter-20261016/evidence.tar.gz','sha256':'db095518788bfafb6cdf0ded3a1172a9e570a14988e48a502d13ab76d71d70f0'},
 {'path':'../prefilter-20261015/evidence-guard-fused-component.tar.gz','sha256':'5bfa6909f40b996b46a10be82657c728511149d0240a75f0e960c224456e0a53'},
 {'path':'../guard-fused-20261016/guard-fused.bin','sha256':'e889e0a6f123a7ae34a9d81339a209ba93aad5246b224057107de3360a9c578a'},
 {'path':'../guard-fused-20261016/guard512.bin','sha256':'5477d190d11716b0769d0d1c681b49368549345e095a71c85fae871e48e14375'},
 {'path':'../guard-fused-20261016/guard-fused.nodeids-u32le.bin','sha256':'60f66061b25cc6b1a4ef7fb4873e0bc77eb84c1017ce53bdb0068fed79d1a91b'},
 {'path':'tool/target/release/value_prefilter','sha256':receipt['binary_sha256']}]}
with tarfile.open(archive,'w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(archive)as t:
 for x in manifest['files']:assert hashlib.sha256(t.extractfile(x['path']).read()).hexdigest()==x['sha256']
summary={'status':'ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY','archive_sha256':sha(archive),'files':len(files),'hashrefs':len(manifest['hashrefs']),'terminal_receipt_sha256':sha(r/'TERMINAL-EVIDENCE-RECEIPT.json')}
(r/'ARCHIVE-RECEIPT.json').write_bytes((json.dumps(summary,indent=2)+'\n').encode());print(json.dumps(summary))
