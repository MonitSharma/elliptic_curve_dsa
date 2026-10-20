review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':len(f['source_files']),'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark reproduction; targets independent Toffoli objective with extra width. Fresh public T minimum checked again immediately before upload.'};save('FINAL-VERIFICATION.json',review)
parent=g['summaries']['parent'];candidate=g['summaries']['candidate'];lease=ws/'breakthrough-context-lease-20261020';lr=json.loads((lease/'context16.json').read_text());assert len(lr['leases'])==213 and all(not scopes for scopes in lr['lease_scopes']);assert json.loads((research/'FINISHED-RESULT.json').read_text())['native_tests']==28;assert json.loads((lease/'RESULT.json').read_text())['native_controls']==7
note=f'''Model: GPT-6 sol
Harness: Codex

#213 exact earlier-context product leases: Q{b['qubits']} / T{b['rounded_mean_executed_toffoli']}

The unchanged challenge benchmark passes all9,024 protected shots at
{b['qubits']} logical qubits and {b['rounded_mean_executed_toffoli']} rounded
mean executed Toffolis, exact mean {b['mean_executed_toffoli']}, total
{b['total_executed_toffoli']}, product {b['product']}.
This improves the direct official Toffoli parent's T750911 by
{750911-b['rounded_mean_executed_toffoli']} rounded Toffolis. Width changes
from1464 to{b['qubits']}; extra width is explicitly accepted for the independent
Toffoli objective. This is not a global product or width record. The current
independent product record is lower. Fresh public minima are checked before upload.
The fresh paired census measures the circuit cost difference at
{g['candidate_minus_parent_mean_executed_toffoli']} Toffolis, paired standard
error {g['paired_standard_error']}; finite-packet variation can affect the rounded gain.

## Direct parent and exact change

Direct public source: official a4ee760a-0500-4d54-9822-4a3c56806fd5,
Q1464/T750911, source be2902c2a133754968dbc97992c753cc08730e83.
All196 public source files and17 protected files were independently verified
as Git objects against locally validated source28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f.
Its entire constructor remains byte-identical, with only its entrypoint renamed.
The new wrapper asserts every canonical record of the complete official parent
before stripping its checked96-X historical nonce8 identity tail. Candidate
arithmetic content is frozen separately at nonce0. The parent's original raw
binding,153-lease cache and exact generic passes remain unchanged.

The earlier arbitrary-cut engine initialized independent values at the first
product, losing input relations prepared immediately before it. The new engine
extends that arbitrary cut backwards by at most4096 operations, staying within
the SAME lexical outer condition scope. It never crosses the enclosing opening
PushCondition. It starts with arbitrary independent quantum/classical values,
executes exact full expression semantics, captures the first effective product
at its original point, and requires exact equality at the second point. Internal
guards and arbitrary measurement outcomes are included. Knowledge caps lose
information conservatively; hashes/fingerprints only nominate, never accept.

The common outer predicate is cofactored true: false skips both endpoints while
the donor remains zero. Identical preparation before the first endpoint means
its value relation holds regardless of incoming phase. Existing donor cleanliness,
no-touch and non-overlap proofs and measurement-based phase repair are unchanged.
Seven native proof controls pass, including prepared aliases, broken-alias faults,
outer-scope boundary rejection, unbalanced guards, every small basis/guard value,
phase, cleanup and executed cost, and deliberate missing-phase fault detection.

On the exact official parent,1877 nominations yield213 fully proved unconditional
leases and1664 unproved rejections. The213 saving is a component diagnostic,
not independently scored. Maximum donor1479 is a capacity observation. No
unproved replacement is included. The final native table binds its complete
input prefix and EVERY canonical output record to the independently generated
proof output. It then runs the unchanged generic exact pipeline and appends
the96-X identity tail. All28 finished-source native controls pass, including
both the inherited153 cache and the new213 cache. Arithmetic, comparison
precision, public140 schedule, square1408 and all inherited correctness cuts
are unchanged. No circuit content was fitted to challenge packets or nonces.

Final source {revision};198 point-add files,17 protected files. Only mod.rs
and new context_finished.rs/context_lease_cache.rs differ from the parent.
Harness, scorer, simulator, curve, Cargo, toolchain and historical results remain
byte-identical, and original Git modes are preserved.
Source archive SHA256 {review['source_archive_sha256']}.
Patch SHA256 {review['source_patch_sha256']}.

## Sole declared final failure-rate gate

Declared at {d['declared_at_utc']}, label {g['label']},32768 batches of64
shots =2097152 fresh shots per source, candidate nonce0. Exact public parent
stream {g['parent_stream_sha256']}; candidate {g['candidate_stream_sha256']}.
Declaration SHA256 {review['gate_declaration_sha256']}.
Result SHA256 {review['gate_result_sha256']}.

|Measurement|Parent|Candidate|
|---|---:|---:|
|Wrong-value shots|{parent['value_shots']}|{candidate['value_shots']}|
|Phase-failing shots|{parent['phase_shots']}|{candidate['phase_shots']}|
|Dirty-ancilla shots|{parent['dirty_shots']}|{candidate['dirty_shots']}|
|Failed batches|{parent['failed_batches']}|{candidate['failed_batches']}|
|Failed batches per9024-shot packet|{parent['failed_batches_per_9024_packet']}|{candidate['failed_batches_per_9024_packet']}|
|Mean executed Toffolis|{parent['mean_executed_toffoli']}|{candidate['mean_executed_toffoli']}|

Newly failing batches b={g['newly_failing_batches_b']}, newly passing
c={g['newly_passing_batches_c']}; one-sided exact McNemar
p={g['one_sided_exact_mcnemar_p']}. Wrong-value failing shot identities equal:
{g['value_failing_shot_identities_equal']}; new value failures
{g['new_value_failing_shots']}, newly passing {g['new_value_passing_shots']}.
All four declared criteria pass: no more value failures than exact parent,
paired p>=0.05, failed batches per packet<=18, zero dirty shots. This gate was
declared and run once. Its verdict is final; no relabel, extension, nonce or
source change reversed failure. Older failed experiments and verdicts stand.

## Frozen-circuit nonce policy and complete benchmark

Only after PASS, ascending nonces from1 were screened. Lowest passing nonce
{k};{len(rows)} production screens,1..{sr['highest_screened']}, passing nonces
{passes}, parallel overrun{k+1}..{sr['highest_screened']} disclosed. The nonce
was never selected by Toffoli count. Eight additional partial-packet controls
1..8 repeat production. This source independently requalifies the unchanged
generic exact engine against24 protected full qubit/classical/phase/RNG states,
curve and partial-mask checks at batches0,70,140. No approximate arithmetic
filter is used. The selected nonce separately passes a complete9024-attempt
protected replay. Final source changes only the new nonce literal from gated
source; every pre-tail record is byte-identical. The unchanged benchmark
rebuilds and passes all9024 shots with zero value, phase and ancilla failures.

Selected stream SHA256 {b['native_receipt']['stream_sha256']}.
Canonical records SHA256 {b['native_receipt']['records_sha256']}.
Pre-tail SHA256 {b['native_receipt']['pre_tail_sha256']}.

Source/patches, all native test logs and deliberate faults, exact proof source,
accepted/rejected rows, stream bindings/hashes, final census declaration and rows,
nonce controls/all screens and benchmark are preserved in the breakthrough-
context-lease-20261020 and related finished/final-gate/nonce/final packages.
Every archive/source member is independently checked locally before submission.
Original source attributions and evidence remain intact. Inherited approximate
arithmetic remains: a finite clean packet is not a universal correctness claim
or an independent novelty claim. Model GPT-6 sol; coding harness Codex;
research attribution MonitSharma.
'''
assert len(note)>6000
for digest in[review['source_archive_sha256'],review['source_patch_sha256'],review['gate_declaration_sha256'],review['gate_result_sha256'],b['native_receipt']['stream_sha256'],b['native_receipt']['records_sha256'],b['native_receipt']['pre_tail_sha256']]:assert digest in note
(r/'SUBMISSION-NOTE.md').write_text(note)
save('DEPENDENCIES.json',[{'submissionId':'a4ee760a-0500-4d54-9822-4a3c56806fd5','rationale':'Direct public constructor and sole exact-parent final gate. Preserve every arithmetic/precision choice and add213 independently exact earlier-context product leases plus unchanged generic pass.','evidence':f"Public sourcebe2902c2; local byte-verified base{f['base']}; final{revision}; archive{review['source_archive_sha256']}; patch{review['source_patch_sha256']}."}])
files={};stream_hashes={}
for prefix,directory in[('',r),('gate',gate),('search',search),('research',research),('lease',lease)]:
 for p in directory.iterdir():
  if p.is_file()and'resource-preflight'not in p.name and p.name not in['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log']:
   name=(prefix+'/'if prefix else'')+p.name
   if p.name.endswith('ops.bin'):stream_hashes[name]=sha(p)
   else:files[name]=p
lf=json.loads((lease/'SOURCE-FREEZE.json').read_text())
for p,h in lf['tool_source_files'].items():assert sha(lease/'tool'/p)==h;files['lease/tool-source/'+p]=lease/'tool'/p
parent_receipt=ws/'breakthrough-public322-square-final-20261020/PUBLIC-SOURCE-VERIFICATION.json';files['parent/PUBLIC-SOURCE-VERIFICATION.json']=parent_receipt
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':stream_hashes,'scope':'Full final source archive, both native cache controls, earlier-cut proof source/rows, sole final paired gate, qualified nonce/all screens and complete unchanged benchmark. Source-review JSON is authoritative; live review stdout omitted. No process listings or credentials.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as archive:
 for n,p in sorted(files.items()):archive.add(p,arcname=n,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
