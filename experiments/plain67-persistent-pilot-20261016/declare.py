from pathlib import Path
import hashlib,json,math,tarfile
R=Path(__file__).resolve().parent;B=R.parent;old=B/'product67-filter-20261016'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(old/'evidence.tar.gz')=='9f3923817a8175babb68ee992bf4da5593ffa3c5c36a6c297b7ad7897b48bfee'
with tarfile.open(old/'evidence.tar.gz')as t:
 manifest=json.load(t.extractfile('manifest.json'))
 for name,h in manifest.items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==h,name
 prefix=t.extractfile('baseline-0.jsonl').read();prefixsha=hashlib.sha256(prefix).hexdigest();assert prefixsha==manifest['baseline-0.jsonl']
 sourcepins={f'/home/hclau/ecdsa_research/product67-filter-20261016/{n}':h for n,h in manifest.items()if n.startswith('tool/')}
common=json.loads((B/'repair67-cost-20261016/LAUNCH_BINDINGS.json').read_text())['artifacts']
keep=['/prefilter-20261015/evidence/mask-freeze-v3.json','/prefilter-20261015/evidence/mr-mask-tip-v3-fused.bin','/prefilter-20261015/evidence/mr-mask-tip-v3.json','/prefilter-20261015/libmask_fused.so','/prefilter-20261015/libsimd8wide.so','/prefilter-20261015/model-source/anchors.txt','/prefilter-20261015/model-source/steps.txt','/product-exact-20261015/tip/ops.bin','/rail-masks-20261016/librail8_masks.so','/scalar-fast-20261015/libscalar_fast_batch.so','/shake8-20261015/libshake8.so','/zero-mr-slice-20261016/libzero8_slice.so','/zero-mr-slice-20261016/tip.compact16.bin']
artifacts={x['path']:x['sha256']for x in common if any(x['path'].endswith(s)for s in keep)};assert len(artifacts)==len(keep)
root='/home/hclau/ecdsa_research/'
artifacts.update({root+'zero-dispatch-20261016/libthreaded.so':'1444e146e9359940123af3b951069c768313947f601d201b4bc391d8ac45cb95',
 root+'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin':'268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d',
 root+'product-exact-20261015/cache-certificate67-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json':'303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6',
 root+'product-exact-20261015/cache-certificate67-20261016/PER_INPUT_MASK_TRANSFER.json':'d774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f',
 root+'product-exact-20261015/cache-certificate67-20261016/PER_INPUT_MASK_TRANSFER.md':'5914f683bb5df08d21f94d79663c6239a84715e27b2eac7e18ce1fcafaee0167',
 root+'product-exact-20261015/PRODUCT67_ABI.json':'2d7f0fc10292ecc815bbf72990bb237ac52b0966aeb9445deee896deed75e510'})
artifacts.update(sourcepins)
(R/'QUALIFICATION-REVIEW.json').write_bytes((old/'ROOT_RUNTIME_VERIFIED.json').read_bytes())
bindings={'executable':root+'product67-filter-20261016/tool/target/release/value_prefilter','executable_sha256':'12fb482e919ba69459d54904ff4370807b61512a280af0a10599c0a242293065',
 'candidate':root+'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin','model_source':root+'prefilter-20261015/model-source','artifacts':artifacts}
(R/'RUNTIME-BINDINGS.json').write_bytes((json.dumps(bindings,indent=2)+'\n').encode())
d={'status':'PREDECLARED_DISABLED_UNCHANGED_PLAIN67_COST_ONLY_PILOT','qualification_archive_sha256':sha(old/'evidence.tar.gz'),'qualification_review_sha256':sha(R/'QUALIFICATION-REVIEW.json'),
 'reference_prefix_path':'baseline-0.jsonl','reference_prefix_sha256':prefixsha,'reference_prefix_nonces':[1,4096],
 'trial_modes':['generic','direct'],'workers_each_trial':2,'threads_each_worker':2,'max_worker_threads':4,'first_each_worker':1,'count_each_worker':16384,'lookahead':4096,'windows_per_startup':4,
 'unique_cost_inputs':16384,'already_qualified_prefix':4096,'new_predetermined_cost_only_inputs':12288,'rows_with_repetitions':65536,
 'pretrial_controls':{'first':4097,'count':11,'lookahead':9,'modes':['generic','direct'],'packed_protected_zeroMR_shadow':True,'generic_full9024_q_b_phase_physicalMR_shadow':True},
 'all_rows_check':'Covered1..4096 prefix equals archived baseline. All16384 complete rows equal across both workers and both modes. New boundary partial controls also equal each other and the matching trial rows.',
 'source_and_binary_changed':False,'Q':1234,'B':54995,'no_A29_or_G_transfer':True,'candidate_failed_batches':4162,'census_batches':32768,'packet_batches':141,
 'expected_nonces_model':math.exp(-141*math.log1p(-4162/32768)),'cost_scope':'Actual four-core group wall includes startup amortized over four windows per worker. Ideal linear64-thread projection multiplies measured throughput by16; it does not measure64-thread scalability.',
 'scalar_library':'Resolved absolute libscalar_fast_batch.so with3bb23042 hash is fixed explicitly, verified before/after and captured from each initialized worker process map.',
 'memory_GiB_each':12,'minimum_available_GiB':124,'overall_timeout_s':900,'CANDIDATE_SEED_SHADOW':True,'proof_accepted':False,'authoritative_rejection':False,'nonce_selected':None,'source_content_tuning':False,'new_eligibility_census':False,'production_changed':False,'search_authority':False}
(R/'DECLARATION.json').write_bytes((json.dumps(d,indent=2)+'\n').encode());print(sha(R/'DECLARATION.json'))
