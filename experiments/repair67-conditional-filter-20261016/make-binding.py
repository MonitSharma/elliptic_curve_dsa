from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
experiments=root.parent
server='/home/hclau/ecdsa_research/'
rel='prefilter-20261015/a29-conditional-certificate-v1/CONDITIONAL_TRANSFER_CERTIFICATE.json'
raw=(experiments/rel).read_bytes();assert hashlib.sha256(raw).hexdigest()=='b351ae4cbf4fab52a8248a83d517502c331a0a4291f73f0123370cad645a2c03'
cert=json.loads(raw)
assert cert['combined_dependency']=='D_new,j(x) = D_original,j(x) OR G(x)'
artifacts=[dict(path=server+rel,sha256=hashlib.sha256(raw).hexdigest())]
for item in cert['proof_receipts']+[cert['public_discrepancy_guard'],cert['ABI']['candidate67_ABI_receipt']]+[cert['A29_relative_cache67'][k] for k in ['universal_certificate','conditional_transfer']]:
    artifacts.append(dict(path=server+item['path'],sha256=item['sha256']))
artifacts.extend([
 dict(path=server+'product-exact-20261015/tip/ops.bin',sha256=cert['original_stream_sha256']),
 dict(path=server+'product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin',sha256=cert['A29_stream_sha256']),
])
# This input path was checked against the frozen server provenance before use.
binding=dict(status='DISABLED_RUNTIME_SOURCE_CHAIN_BINDING_ONLY',candidate_stream=cert['A29_relative_cache67']['candidate_stream_sha256'],conditional_theorem_sha256=hashlib.sha256(raw).hexdigest(),combined_dependency=cert['combined_dependency'],artifacts=artifacts,no_runtime_or_search_authority=True)
(root/'COMPOSITE_BINDING.json').write_text(json.dumps(binding,indent=2)+'\n')
print(json.dumps({'artifacts':len(artifacts),'manifest_sha256':hashlib.sha256((root/'COMPOSITE_BINDING.json').read_bytes()).hexdigest()}))
