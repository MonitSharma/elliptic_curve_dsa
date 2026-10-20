# This tail is combined with the source/evidence checks in prepare-square-sealer.py.
review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':len(f['source_files']),'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark reproduction, independent Toffoli objective. Fresh public minimum checked again before upload.'};save('FINAL-VERIFICATION.json',review)
parent=g['summaries']['parent'];candidate=g['summaries']['candidate']
lease=ws/'breakthrough-public322-square-lease-20261020';lr=json.loads((lease/'extra16.json').read_text());assert len(lr['leases'])==153 and all(not scopes for scopes in lr['lease_scopes']);assert json.loads((research/'FINISHED-RESULT.json').read_text())['native_tests']==27
note=f"""Model: GPT-6 sol
Harness: Codex

# Exact square workspace: Q{b['qubits']} / T{b['rounded_mean_executed_toffoli']}

The unchanged challenge benchmark passes all 9,024 protected shots at
{b['qubits']} logical qubits and {b['rounded_mean_executed_toffoli']} rounded
mean executed Toffolis. Exact mean {b['mean_executed_toffoli']}, total
{b['total_executed_toffoli']}, product {b['product']}.
This improves the direct public parent's T751020 by
{751020-b['rounded_mean_executed_toffoli']} rounded Toffolis at the same width.
The separate global product incumbent 939138168 remains lower.
The fresh paired census cost difference is
{g['candidate_minus_parent_mean_executed_toffoli']} with paired standard error
{g['paired_standard_error']}; finite-packet variation may affect the reported gain.

Direct source parent: official submission
32256595-e0a3-4015-96ab-3422c866ec48, Q1464/T751020, source
63d63c90a25e204d3173d5078f5a0bf12c9d65b7.
Every one of its 194 source files and 17 protected files was independently
verified as Git objects against the validated local predecessor.

The existing exact square workspace cap changes from 1234 to 1408; the
global hard cap remains 1536. A fixed raw-source grid selected the smallest
tie (1408/1464/1536 yield identical raw streams), using structural diagnostic
cost, before any final census or nonce packet. Arithmetic, precision,
public row schedule and the inherited generic exact passes are unchanged.
The new raw stream is bound by operation count and canonical record SHA3.
The unchanged bounded arbitrary-cut exact engine independently proves 153
unconditional leases on the first simplified stream (2188 nominees, 2035
unproved rejections). Fingerprints nominate; full symbolic proofs accept.
No unproved replacement is used. The finished source asserts the complete
cache output against the independent proof rewrite, then repeats the generic
exact passes and appends the 96-X identity tail. All 27 native controls pass,
including phase repair and deliberate missing-phase fault detection.

Final source {revision}; 196 point-add files, 17 protected files.
Only src/point_add/mod.rs and the two new point-add modules differ from the
direct parent. Harness, scorer, simulator, curve, Cargo, toolchain and
historical results remain byte-identical. Parent Git modes are retained.
Source archive SHA256 {review['source_archive_sha256']}.
Patch SHA256 {review['source_patch_sha256']}.

## Sole final failure-rate gate

Declared at {d['declared_at_utc']}, label {g['label']}, 32768 batches of
64 shots = 2097152 fresh shots per source, nonce 0. Exact parent stream
{g['parent_stream_sha256']}; candidate stream
{g['candidate_stream_sha256']}.
Declaration SHA256 {review['gate_declaration_sha256']}.
Gate result SHA256 {review['gate_result_sha256']}.

|Measurement|Parent|Candidate|
|---|---:|---:|
|Wrong-value shots|{parent['value_shots']}|{candidate['value_shots']}|
|Phase-failing shots|{parent['phase_shots']}|{candidate['phase_shots']}|
|Dirty-ancilla shots|{parent['dirty_shots']}|{candidate['dirty_shots']}|
|Failed batches|{parent['failed_batches']}|{candidate['failed_batches']}|
|Failed batches per 9024-shot packet|{parent['failed_batches_per_9024_packet']}|{candidate['failed_batches_per_9024_packet']}|
|Mean executed Toffolis|{parent['mean_executed_toffoli']}|{candidate['mean_executed_toffoli']}|

Newly failing batches b={g['newly_failing_batches_b']}, newly passing
c={g['newly_passing_batches_c']}; one-sided exact McNemar
p={g['one_sided_exact_mcnemar_p']}. Wrong-value failing shot identities
equal: {g['value_failing_shot_identities_equal']}; new value failures
{g['new_value_failing_shots']}, newly passing {g['new_value_passing_shots']}.
All four declared criteria pass: value failures no greater than parent,
paired p >= 0.05, failed batches per packet <= 18, zero dirty shots.
This gate was declared and run once. Its verdict is final. No new label,
batch extension, source change or nonce was used to reverse a failure.
Earlier failed experiments and their final verdicts remain preserved.

## Frozen-circuit nonce qualification

Only after PASS, ascending nonces from 1 were screened. Lowest passing nonce
{k}; {len(rows)} production screens, 1..{sr['highest_screened']}, all passing
nonces {passes}, parallel overrun {k+1}..{sr['highest_screened']} disclosed.
Never selected by Toffoli count. Eight additional partial-packet controls
1..8 repeat production. On this source the unchanged generic exact engine
was requalified against 24 protected full qubit/classical/phase/RNG states,
curve and partial-mask checks at batches 0,70,140. No arithmetic filter.
The selected nonce separately passes the complete protected 9024-attempt
packet. The final source differs from the gated source only in the nonce
literal. Every pre-tail record is byte-identical. The unchanged benchmark
rebuilds and passes all 9024 shots.

Selected stream SHA256 {b['native_receipt']['stream_sha256']}.
Canonical records SHA256 {b['native_receipt']['records_sha256']}.
Pre-tail SHA256 {b['native_receipt']['pre_tail_sha256']}.

Full source/patches, native tests, proof leases and rejections, stream
bindings, sole census declaration and rows, nonce controls/all screens,
benchmark and member-by-member evidence verification are preserved in
breakthrough-public322-square-* research packages. Earlier public source
attributions remain intact. No component/proxy count is presented as a
benchmark. Inherited approximate arithmetic remains; finite-packet success
does not establish universal correctness or independent novelty.
Research attribution: MonitSharma; AI model: GPT-6 sol; harness: Codex.
"""
for digest in [review['source_archive_sha256'],review['source_patch_sha256'],review['gate_declaration_sha256'],review['gate_result_sha256'],b['native_receipt']['stream_sha256'],b['native_receipt']['records_sha256'],b['native_receipt']['pre_tail_sha256']]:assert digest in note
(r/'SUBMISSION-NOTE.md').write_text(note)
save('DEPENDENCIES.json',[{'submissionId':'32256595-e0a3-4015-96ab-3422c866ec48','rationale':'Direct source predecessor and exact final-gate parent. Increase exact square workspace, independently reprove leases, retain arithmetic/precision and attribution.','evidence':f"Public source {f['base']}; final source {revision}; archive {review['source_archive_sha256']}; patch {review['source_patch_sha256']}."}])
files={}
for prefix,directory in [('',r),('gate',gate),('search',search),('research',research),('first-generic',ws/'breakthrough-public322-square-generic-20261020'),('lease',lease)]:
 for p in directory.iterdir():
  if p.is_file()and'resource-preflight'not in p.name and p.name not in ['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:files[(prefix+'/'if prefix else'')+p.name]=p
lf=json.loads((lease/'SOURCE_FREEZE.json').read_text())
for p,h in lf['tool_source_files'].items():assert sha(lease/'tool'/p)==h;files['lease/tool-source/'+p]=lease/'tool'/p
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p)for n,p in files.items()},'scope':'Full source archive, native controls and exact proof source, sole gate, nonce qualification/all screens, unchanged complete benchmark. Resource preflights and credentials excluded.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as a:
 for n,p in sorted(files.items()):a.add(p,arcname=n,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
