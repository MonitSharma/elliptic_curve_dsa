from pathlib import Path,PureWindowsPath
import datetime,hashlib,json,math,re
root=Path(__file__).resolve().parent;workspace=root.parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
assert not (root/'ACCEPTANCE.json').exists()
review=workspace/'prefilter-20261015/review/operational-review-v2.json';assert sha(review)=='a53ced524261db8de42913da30eb3dd2cccfe5f00a1d93e92f346e9cbee94312'
for name,expected in read(review)['reviewed_files'].items():
 path=workspace.joinpath(*PureWindowsPath(name).parts[1:]);assert sha(path)==expected,name
assert (root/'build.exit').read_text().strip()=='0'
assert '1 passed; 0 failed' in (root/'order-v2-tests.log').read_text()
up=workspace/'product-exact-20261015';census=read(up/'product25-census-summary.json')
assert census['measured_failure_gate_pass'] and census['candidate']['failed_batches']<=census['parent']['failed_batches']
assert census['candidate']['failures_per_packet']<=18
cert=up/'cache-certificate-v2-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json'
assert sha(cert)=='4857f8255c6aa85f0c6cb84720c6d5690aaca060f2758a8c517bd43fc5e2f04e'
assert read(cert)['status']=='UNIVERSAL_CACHE_EQUIVALENCE_AUDIT_PASS'
required={
 up/'candidate-product-final25/ops.bin':'180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64',
 workspace/'prefilter-20261015/evidence/mr-mask-tip-v3.bin':'560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d',
 workspace/'prefilter-20261015/evidence/mr-mask-tip-v3-fused.bin':'1ccbbfc4a45b8d359be9ce21eb4640c72bb9bfe9bffb35f5630c0d13da3f2f8a',
 workspace/'prefilter-20261015/libmask_fused.so':'dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0',
 workspace/'scalar-fast-20261015/libscalar_fast_batch.so':'3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'}
for path,expected in required.items():assert sha(path)==expected,path
for folder,status in [('product-mask-filter-20261016','BOUNDED_CANDIDATE25_SOURCE_TRANSFER_INTEGRATION_PASS'),('product-fused-filter-20261016','FUSED_CANDIDATE25_BOUNDED_ROWS_EXACT_PASS'),('product-early-filter-20261016','EXACT_EARLY_FULLSTATE9024_AND_ROWS4096_PASS')]:assert read(workspace/folder/'RESULT.json')['status']==status
transfer=[read(workspace/'prefilter-20261015/evidence'/f'mask-validate-transfer-{name}.json') for name in ['audit','all-failing-tip','sensitivity-structured','sensitivity-arbitrary']]
assert sum(r['shots'] for r in transfer)==2214 and all(r['candidate_protected_vs_original_zeroMR_known_bit_containment_passed'] for r in transfer)
costroot=workspace/'product-early-cost-20261016';cost=read(costroot/'RESULT.json');assert cost['status']=='BOUNDED_FOUR_PROCESS_COST_MEASUREMENT_PASS'
walls=[float(re.search(r'wall_seconds=([0-9.]+)',(costroot/f'worker{lane}.log').read_text()).group(1)) for lane in range(4)]
mean_nonces=math.exp(-141*math.log1p(-census['candidate']['failures_per_packet']/141))
seconds_per_nonce=sum(walls)/(4*262144);steady48=mean_nonces*seconds_per_nonce/3600;startup48=mean_nonces*cost['wall_including_four_startups_seconds']/262144/3600
assert steady48<=24 and startup48<=24
record={'status':'SOURCE_BOUND_MASK_TRANSFER_AND_RUNTIME_ACCEPTED_FOR_ASCENDING_SEARCH','accepted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_stream_sha256':required[up/'candidate-product-final25/ops.bin'],'mask_sha256':required[workspace/'prefilter-20261015/evidence/mr-mask-tip-v3.bin'],'lowest_pass_from':1,'submission_mode':'queue','failure_gate_pass':True,'cost_gate_pass':True,'census':census,'expected_nonces':mean_nonces,'measured_expected_hours_48threads':{'steady':steady48,'including_startup_per_timing_packet':startup48},'ideal64thread_projection_hours':{'steady':steady48*48/64,'startup':startup48*48/64},'four_worker_wall_seconds':walls,'root_semantic_review':'Universal source-bound input-conditioned dependency upper bounds; immutable input-only cap definitions; wrong originalzeroMR output bit only when known; completed universal25 cache equivalence/per-input transfer; candidateownFiat and exactfull fallback. Sampled replay supplements this argument. Trusted Boolean/decoder/HMR-CZ kernel, not a proof-assistant proof.','independent_operational_review_sha256':sha(review),'universal_certificate_sha256':sha(cert),'runtime_artifacts':{str(p):h for p,h in required.items()},'remaining_gates':['Every lower nonce disposition accounted before selecting lowestpass','Unchanged full native benchmark on selected final source','Final predeclared failure census and identity-tail prefix audit'],'score':None}
(root/'ACCEPTANCE.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'status':record['status'],'sha256':sha(root/'ACCEPTANCE.json'),'steady48_hours':steady48,'startup48_hours':startup48},indent=2))
