from pathlib import Path
import json,hashlib,struct,itertools
r=Path(__file__).resolve().parent
owner=r.parents[2]/'quantum-borrow-family-20261016'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((r/'classical-interface-proof.json').read_text())
assert proof['proved'] and len(proof['sites'])==12
assert proof['tests']['programs']==28 and proof['tests']['exhaustive_scalar_cases']==904
meta=json.loads((owner/'native-verification.json').read_text())
assert meta['sha256']=='12840968ed58bb2063128d133a8f493bce3ed90256ee3b03bb5dcdc3f40dc30e'
assert meta['parent_sha256']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
assert meta['all12_regions_exact'] and meta['all_unrelated_operations_byte_identical']
prefix=json.loads((owner/'flag-prefix-zero-receipt.json').read_text())
assert prefix['proved'] and prefix['source_sha256']==meta['parent_sha256']
assert len(prefix['results'])==12 and all(not x['unresolved'] for x in prefix['results'])
abi=json.loads((r.parents[1]/'evidence/a29-feasibility-abi.json').read_text())['original_ABI']
assert [[x[1]for x in ws]for ws in abi]==[list(range(256)),list(range(256,512)),list(range(256)),list(range(256,512))]
bodyhash=json.loads((owner/'quantum-proof-source-hashes.json').read_text())['src/quantum_phase_body.rs']
assert sha(r/'quantum_phase_body.rs')==bodyhash
for j in range(12):
 for mode in ['old','new']:
  x=json.loads((owner/f'{mode}-quantum-contract-{j}.json').read_text())
  assert x['phase_contract_proved'] and not x['q_contract_unresolved'] and x['outer_caps']==0
  assert set(x['clean_scratch_preconditions'])==set(prefix['results'][j]['scratch'])
data=(r/'quantum_flag.bin').read_bytes();assert data[:8]==b'QFLAG001';at=16
for j in range(12):
 n,m=struct.unpack_from('<QQ',data,at);at+=16
 old=list(struct.iter_unpack('<7Q',data[at:at+56*n]));at+=56*n
 new=list(struct.iter_unpack('<7Q',data[at:at+56*m]));at+=56*m
 assert not any(row[0]in[1,2] for row in old+new),'helper changes ABI metadata'
assert at==len(data)
for a,b,s,m,g in itertools.product([0,1],repeat=5):
 majority=((1^a)&b)^((1^a)&s)^(b&s)
 cleanup=b^s^(a&b)^(a&s)^(b&s)
 assert majority==cleanup and (m&g&majority)^(m&g&cleanup)==0
report=dict(status='INDEPENDENT_READ_ONLY_REVIEW_SUPPORTS_CONDITIONAL_COORDINATE_MASK_TRANSFER',material_findings=[],classical_interface_reproduced=True,all12_cases=True,quantum_contract_source_hash=bodyhash,original_ABI_covers_prefix_unknowns=True,source_native_binding_reviewed=True,transfer_theorem='For each full candidate MR tape, delete the12 inserted cleanup draws. Arbitrary old classical entry state and enclosing snapshot produce identical old bit outputs; independently proved clean-carry q restoration produces identical q outputs. Untouched operations compose inductively. Thus candidate coordinates equal original coordinates on the projected old tape, and every original input-conditioned MR-free scored bit remains MR-free in the candidate.',required_new_certificate=['original and candidate stream hashes','original mask/proof hashes and physical input/output port maps','all12 actual helper blob hashes and exact native outside-region identity','globally proved carry-zero preconditions and induction through prior q restorations','arbitrary-entry classical transducer and complete MR projection including inactive draws','new-bit namespace disjointness'],not_claimed=['same unprojected physical MR tape','phase equality or failure-rate transfer','candidate Fiat seed equality','new source-chain certificate issued','runtime integration or production search changes'],review_scope='Code and receipts reviewed; exact classical interface rerun independently. The24 Rust quantum contracts and full native stream verifier were inspected, not rerun by this reviewer.')
(r/'REVIEW.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
