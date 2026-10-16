"""Append-only metadata binding audit; does not replace the universal checker."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
paths={
 'base53':r/'repair53-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json',
 'append':r/'repair67-universal-20261016/RECEIPT.json',
 'final67':r/'repair67-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json',
 'native':r/'repair67-native-20261016/NATIVE_RECEIPT.json',
 'freeze':r/'REPAIR67_FREEZE.json',
}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d={k:json.loads(p.read_text()) for k,p in paths.items()}
b,a,c,n,f=[d[k] for k in ('base53','append','final67','native','freeze')]
assert sha(paths['base53'])==a['preceding53_certificate_sha256']==c['preceding53_certificate_sha256']
assert sha(paths['append'])==c['append_receipt_sha256']
assert sha(paths['native'])==a['native_receipt_sha256']==c['native_receipt_sha256']
assert sha(paths['freeze'])==a['source_freeze_sha256']==c['source_freeze_sha256']
assert b['baseline_stream_sha256']==a['baseline_stream_sha256']==c['baseline_stream_sha256']==f['repair_parent_sha256']
assert b['candidate_stream_sha256']==a['intermediate53_stream_sha256']==a['stages'][0]['input_sha256']
assert [s['stage'] for s in a['stages']]==list(range(54,68))
for prev,cur in zip(a['stages'],a['stages'][1:]):assert prev['output_sha256']==cur['input_sha256']
assert all(s['status']=='PASS' and s['returncode']==0 for s in a['stages'])
assert a['stages'][-1]['output_sha256']==a['candidate_stream_sha256']==c['candidate_stream_sha256']==n['native_stream_sha256']
assert b['leases_verified']+c['append_leases_verified']==c['leases_verified']==245849
assert b['replaced_uses_verified']+c['append_replaced_uses_verified']==c['replaced_uses_verified']==540826
out=paths['final67'].parent/'COMPOSITION_METADATA_AUDIT.json'
assert not out.exists()
out.write_text(json.dumps(dict(status='APPEND_ONLY_METADATA_BINDINGS_PASS',artifact_sha256={k:sha(p) for k,p in paths.items()},stage_count=67,leases=245849,replaced_uses=540826,scope='Checks source-bound theorem composition metadata and native endpoint identity. Universal stage obligations remain in the immutable certificates and hashed checker logs; this audit adds no arithmetic equivalence or global measurement-independence claim.'),indent=2)+'\n')
print(out)
