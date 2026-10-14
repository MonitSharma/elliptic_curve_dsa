"""Freeze finite real-prefix all-future-MR proof; strict audit remains unchanged."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[3];folder=Path(__file__).parent;raw=root/'research-output/overnight-20261014/product/rail109-audit'
assert int((raw/'run.exit').read_text())==0
log=(raw/'run.log').read_text();assert 'test result: ok. 7 passed' in log and 'PRODUCT_RAIL109_TOTAL' in log and log.count('PRODUCT_RAIL109_FINAL_GUARD ')==10
rows=[]
for line in log.splitlines():
 if line.startswith('RAIL109_ALLMR '):rows.append(dict(re.findall(r'(\w+)=(\S+)',line)))
assert len(rows)==2
for r in rows:assert (r['ops'],r['cases'],r['measurements'],r['nonconstant_q'],r['phase_terms'])==('3708','15','201','0','0')
archive=(root/'experiments/overnight-20261014/coordinator/phase-polynomial-v1.rs').read_bytes();detail=(folder/'rail109-detail-kernel.rs').read_bytes();assert detail.startswith(archive)
delta=detail[len(archive):];(folder/'rail109-kernel-extension.rs').write_bytes(delta)
doc=dict(status='COMPLETED_FINITE_ALL_FUTURE_MEASUREMENT_PROOF',qualified_score=None,exit=0,native_tests=7,
 native_sha256=(raw/'native.sha256').read_text().split()[0],source_attestation=(raw/'source.sha256').read_text(),input_attestation=(raw/'input.sha256').read_text(),
 strict_kernel_original_sha256=hashlib.sha256(archive).hexdigest(),strict_kernel_byte_prefix_unchanged=True,
 detail_kernel_sha256=hashlib.sha256(detail).hexdigest(),extension_sha256=hashlib.sha256(delta).hexdigest(),
 canonical_kernel_unchanged_sha256='d41de327f9e2162d8009235c77780f3a996351d57aed2011497ee1c6b5e4f035',
 rows=rows,constant_quantum_slots={'c5_raw':1234,'b3_raw':1235},
 claim='For15 real native prefix basis contexts per source, all final quantum values of unchanged R109 slice3708ops are constant for every assignment of201 internal measurement outcomes, and its incremental phase polynomial is exactly zero. Each output constant equals the original whole-prefix native result. In particular point249 retains its wrong rail value for all future internal MR outcomes.',
 domain='Past measurement outcomes are FIXED by original unchanged final-raw prefix and saved15point packet/replaydomain; not quantified. Input phase is additive. Exact q/b arrays are computed by the source-attested original native prefix; reconstruction recipe, source, native, streams, packet and seed domain are preserved. This is not a whole-point ALLMR or arbitrary-input proof.',
 preservation='Original strict audit and all4 native/fault tests are an exact byte prefix. Separate diagnose function exposes phase terms and constant/nonconstant outputs; no strict failure is reinterpreted. Canonical shared file unmodified.',
 independent_oracle='New test compares full native simulator quantum/phase outputs and evaluates exported polynomial on0/all1/A5measurement assignments; planted measurement-dependent quantum/phase faults detected. Two existing frame/overlay mutation tests also pass.',
 full_replay_guard='All271 source point final raw coordinates and phase equal separately archived continuous transcript replay. Exact copied Y33 transformation and both prefix hash domains remain required.',
 artifact_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in raw.iterdir()if p.is_file()})
(folder/'rail109-audit-receipt.json').write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
md='''# Measurement-independent rail109 overflow

The unchanged3708-operation multiply rail tick109 was audited on all fifteen real prefix basis states from the saved known-failure packet, separately for original C5 and B3. Every one of201 internal reset/HMR outcomes is an independent symbolic variable. Final quantum values are constant across all those outcomes; the incremental phase polynomial is identically zero. All1234/1235 output constants exactly equal the original whole-prefix native results. In particular, point249's incorrect rail value is independent of every future measurement within this tick.

This is a finite entry-state proof. Past measurement outcomes are fixed by the original prefix's recorded replay domain. Incoming phase is additive. It does not quantify past outcomes, prove arbitrary input states or establish whole-point phase correctness. Entry quantum/classical arrays are computed from the source-attested original simulator prefix; complete stream/packet/seed/source/native bindings preserve the deterministic reconstruction recipe.

The archived strict kernel `330d91852ddc82740ac9bec4b8d8fb94d2ca5c5ca843fd4e56d1fed6123fab98` is retained as an exact byte prefix, including its original strict audit and four native/fault tests. An appended separate diagnostic exposes polynomial terms and output constants without weakening that audit. The shared canonical kernel remains unchanged. Seven native tests pass: the four original tests, two frame/overlay fault tests and a new independent simulator oracle that evaluates phase polynomials and detects measurement-dependent quantum/phase faults. Exact extension bytes are separately archived.

All271 points per source still reproduce the separately archived final raw coordinates and phase. Original complete source streams, all binding checks and protected files remain unchanged. No score or repair is claimed. The finite integer overflow certificate remains in `rail109-certificate.json`.
'''
md+='\nBinary SHA256 `'+doc['native_sha256']+'`; full source/input/evidence bindings in `rail109-audit-receipt.json`.\n'
(folder/'rail109-audit-results.md').write_text(md,encoding='utf-8',newline='\n')
print(json.dumps(dict(native=doc['native_sha256'],kernel=doc['detail_kernel_sha256'],extension=doc['extension_sha256'])))
