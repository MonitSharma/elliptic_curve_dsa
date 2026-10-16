"""Freeze a separately named per-input theorem only after universal67 completes."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate67-20261016';certificate=d/'CACHE_EQUIVALENCE_CERTIFICATE.json';cert=json.loads(certificate.read_text());assert cert['status']=='UNIVERSAL_CACHE_EQUIVALENCE_AUDIT_PASS' and cert['stage_count']==67
assert not (d/'PER_INPUT_MASK_TRANSFER.json').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();freeze=json.loads((r/'PRODUCT67_FREEZE.json').read_text())
row={'status':'CONDITIONAL_PER_INPUT_MASK_TRANSFER','cache_equivalence_certificate_sha256':sha(certificate),'baseline_stream_sha256':cert['baseline_stream_sha256'],'candidate_stream_sha256':cert['candidate_stream_sha256'],'audited_identity_tail_prefix':freeze['prefix_manifest'],'statement':'For each fixed original ABI input x and scored coordinate bit b, audited equivalence is G_b(x,s)=F_b(x,pi(s)) for every candidate MR vector s. If a separate sound source-bound certificate proves F_b(x,r) constant for every original MR vector r for this x,b, then G_b(x,s)=F_b(x,0) for every s. This per-input premise does not require global MR independence.','separate_premises':['The mask certifies every original MR assignment for this exact input and bit, and is bound to original4b stream hash.','The value evaluator exactly computes the original source function with all original MR bits zero.','The expected curve output and every evaluated input derive from the final candidate own Fiat preparation, including its final nonce.'],'safe_rejection':'A certified masked-bit mismatch to the correct reference curve value proves failure on this input regardless of candidate MR. Uncertified bits, matching bits and empty masks do not prove a full pass.','nonce_scope':'A nonce change must preserve the audited pre-tail operations byte for byte, followed by48 adjacent XX identity pairs. Validate these exact bytes/shape and use the final candidate own Fiat inputs. Never reuse a packet belonging to another source.','remaining_validation':'Full exact simulator handles survivors, including every unproved bit, phase and dirty scratch; unchanged official benchmark remains required.','does_not_certify':['mask or value-model implementation','global original coordinate MR independence','phase independence','any arithmetic precision repair changing F','a full resource record'],'score':None}
(d/'PER_INPUT_MASK_TRANSFER.json').write_text(json.dumps(row,indent=2)+'\n')
text=f'''# Per-input conditional-mask transfer for frozen67

Certificate SHA256: `{sha(certificate)}`.
Original stream: `{cert['baseline_stream_sha256']}`.
Candidate stream: `{cert['candidate_stream_sha256']}`.

For a fixed ABI input x and scored output bit b, the audited chain establishes
G_b(x,s) = F_b(x,pi(s)) for every candidate measurement vector s. If a separate
sound certificate proves that F_b(x,r) is constant for every original
measurement vector r for this particular x and b, then G_b(x,s) = F_b(x,0)
for every s. This needs no global measurement-independence theorem.

A certified masked-bit mismatch between the exact original zero-measurement
value and the reference curve result therefore safely rejects this input.
The mask and evaluator need their own exact source-bound proofs. Matching
values, unproved bits and empty masks do not establish a full pass. Survivors
still require exact phase, scratch and complete output checks, and the final
unchanged official benchmark.

Every input must come from the final candidate's own Fiat preparation. A
nonce change additionally requires byte-identical audited pre-tail operations
and48 adjacent XX identity pairs, using that final source's inputs. This does
not transfer across a precision repair changing the original value function.
The associated JSON binds the exact67 prefix and lists all separate premises.
No source, nonce or certificate is modified by this companion.
'''
(d/'PER_INPUT_MASK_TRANSFER.md').write_text(text)
print(json.dumps({p.name:sha(p) for p in [d/'PER_INPUT_MASK_TRANSFER.json',d/'PER_INPUT_MASK_TRANSFER.md']}),flush=True)
