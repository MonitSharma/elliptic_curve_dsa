review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':200,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark reproduction of fixed exact rail+G6 port. Fresh public minimum checked before upload. Global product objective remains separate.'};save('FINAL-VERIFICATION.json',review)
parent=g['summaries']['parent'];candidate=g['summaries']['candidate'];ports=ws/'breakthrough-exact-native-ports-v3-20261020';development=ws/'breakthrough-exact-ports-development-20261020';pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['both'];assert pc['target_differences_confined_to_both_value_failing']and len(pc['different_target_lanes'])==7 and not pc['different_other_lanes']and not pc['new_value_failing_shots'];assert json.loads((research/'FINISHED-RESULT.json').read_text())['native_tests']==27
note=f'''Model: GPT-6 sol
Harness: Codex

# Exact native rail strip and fold-phase erase: Q{b['qubits']} / T{b['rounded_mean_executed_toffoli']}

The unchanged benchmark rebuilds this fixed source and passes all9,024 protected
shots at {b['qubits']} logical qubits and {b['rounded_mean_executed_toffoli']}
rounded mean executed Toffolis. Exact mean {b['mean_executed_toffoli']}, total
{b['total_executed_toffoli']}, product {b['product']}.
Relative to the exact public final-gate T parent260b3ba0 (Q1480/T750705), this
uses {1480-b['qubits']} fewer qubits and {750705-b['rounded_mean_executed_toffoli']}
fewer rounded Toffolis. Relative to source predecessor a4ee (Q1464/T750911),
the width is unchanged and the rounded saving is
{750911-b['rounded_mean_executed_toffoli']}. These are independent T-front
comparisons. The separate global product record remains lower; no global
product or width record is claimed here. The public T minimum is checked again
immediately before upload. Paired fresh census cost difference is
{g['candidate_minus_parent_mean_executed_toffoli']}, paired standard error
{g['paired_standard_error']}; packet variation affects rounded measurements.

## Source lineage and exact native techniques

Arithmetic source predecessor: official a4ee760a-0500-4d54-9822-4a3c56806fd5,
public be2902c2a133754968dbc97992c753cc08730e83, locally byte-verified
28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f. All196 source files and17 protected
files were checked against official Git objects. We retain its strengthened
uniform+2 comparisons, exact public140 schedule, plain pool, square1408 and
global1536 workspace. No arithmetic precision, new cut or weaker window is used.

The two native techniques come directly from official e3b5c51f-74e6-480a-82bf-
5543fb1ba555 (stack-v3), source88869d8cc23fb72120dd52533f3e48277e9b36e4.
Its original source/note attributions remain intact. We adopt only its disclosed
exact rail R1/R2/EXT2 transformation and G6-prime top-column x257 phase erase.
We do not adopt its G1M square,21-bit witness, approximate T0W/RT0W windows,
recipe retunes, expanded C3 choices or re-anchored postpass table.

Rail port: all native leapfrog diff hunks except the retained-AND recipe retune,
plus the two unchanged public strip netlists. The strip represents letter-
controlled shifts through three reflections, absorbs sign fill, and handles the
exact R1 low-bit garbage and its reverse. G6 port: only the published body
replacement, using a top-column majority identity instead of rebuilding a long
carry chain for x257's phase. A branch-scoping integration repair returns the
original BitId to its unchanged outer cleanup; the arithmetic block is unchanged.

All old bound modules and assertions remain unchanged. Their old input tables
are unused after the new native circuit; no table was shifted or rehashed to
force a binding. The old153-lease table is also unused and no old row index is
transferred. This final circuit has a pure new finish: bind EVERY raw operation
to the frozen native both case, apply the unchanged generic exact passes, bind
EVERY generic output operation to the independently produced research stream,
then append the96-X identity tail. The mode is fixed in source; no external
input file, dump or runtime case selector is used by the final constructor.

## Native controls and full-output development comparison

The new strip control passes6,416,896 native lanes: all valid signed inputs
through16bits, larger samples at17,18,25,26,31,32,63,64, forward and inverse,
every garbage-letter combination and four measurement patterns. It checks full
quantum values, clean helpers and phase. Deleting phase repairs is detected in
55,256 batches. This is a component control, not a full point-add theorem.
The fixed finished source repeats27 native controls including the retained
arithmetic/phase contracts. All pass.

Four source cases were frozen before any new development inputs: original
control, rail-only, G6-only and both. The control raw is exactly the predecessor's
10543037 canonical records/SHA318f7fc00. A single predeclared512-batch x64
fresh-input comparison includes all four and exact public a4ee, with8 protected
scalar batches per stream and complete output/other-ancilla lane hashes.
Every source has18 wrong-value shots, zero dirty shots and no newly wrong-value
shot IDs. G6/control have no target differences. Rail/both have7 target
differences, all confined to inputs where BOTH circuits already fail value;
other-ancilla differences are zero. Both has the lowest structural cost and
development mean, about2227 fewer T than a4ee. Those development counts are
not scored results or a substitute for the separate final gate below.

The native circuit remains approximate through inherited code. Exact component
identities rely on their input contracts; the7 joint-failure differences are
disclosed rather than treated as universal equality. No circuit was fitted to
these development inputs or to challenge packets. Original parser, compile and
missing-environment integration failures are preserved with their source/logs.

Final source {revision};200 point-add files,17 protected files. Only seven
point-add paths differ from the validated source predecessor: mod.rs,
leapfrog.rs,y15_onefold.rs,the two public strip netlists, an unused preserved
research wrapper, and the pure new native_both_finished.rs. Harness, scorer,
simulator, curve, Cargo, toolchain and historical results remain byte-identical;
parent Git modes are preserved. Source archive SHA256
{review['source_archive_sha256']}; patch SHA256 {review['source_patch_sha256']}.

## Sole declared final failure-rate gate

Exact comparator: public260b3ba0-d604-4f0d-9d55-934055d216b4, Q1480/T750705.
Its198 source files and17 protected bytes were checked against official Git
objects before this declaration. This is the record comparator; its213 cache
is not a code dependency of the native port. Declared at {d['declared_at_utc']},
label {g['label']},32768 batches x64 =2097152 fresh shots per source, nonce0.
Exact parent stream {g['parent_stream_sha256']}.
Candidate stream {g['candidate_stream_sha256']}.
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
p={g['one_sided_exact_mcnemar_p']}. Wrong-value shot identities equal:
{g['value_failing_shot_identities_equal']}; new value-failing shots
{g['new_value_failing_shots']}, newly passing {g['new_value_passing_shots']}.
All four criteria pass: value count no greater than parent, paired p>=0.05,
failed batches per packet<=18, zero dirty shots. This source has one declared
final gate. Its verdict is final: no relabel, extension, source or nonce change
reversed failure. Historical failed gates stand. The context213 and development
gates are different sources/tests and are not reused as this verdict.

## Qualified frozen-source nonce and unchanged benchmark

After PASS, ascending nonces from1 were screened. Lowest passing nonce{k};
{len(rows)} production screens,1..{sr['highest_screened']}; passing nonces
{passes}; overrun{k+1}..{sr['highest_screened']}. No nonce is chosen by T.
Eight additional partial-packet controls1..8 repeat production;24 protected
full qubit/classical/phase/RNG states, curve and partial-mask controls use
batches0,70,140. This exact source independently requalifies the frozen generic
exact engine; no approximate arithmetic filter is used. The selected nonce
passes a complete protected9024-attempt replay. Final source changes only its
nonce literal. The unchanged benchmark performs the selected-source rebuild
and passes all9024 shots, zero classical/phase/ancilla failures. Every final
pre-tail byte is checked against the gated nonce0 stream after that rebuild.

Selected stream SHA256 {b['native_receipt']['stream_sha256']}.
Canonical records SHA256 {b['native_receipt']['records_sha256']}.
Pre-tail SHA256 {b['native_receipt']['pre_tail_sha256']}.

All source patches, raw/output bindings, native tests/faults, development full
outputs, sole gate declaration/rows, nonce controls/all screens, benchmark and
member-by-member local source/evidence checks are preserved in the native-both,
exact-native-ports-v3 and exact-ports-development20261020 packages. A finite
clean packet is not a universal correctness or independent novelty claim.
Research attribution MonitSharma; AI model GPT-6 sol; harness Codex. Credit to
the a4ee lineage and stack-v3 authors is retained explicitly.
'''
assert len(note)>6000
(r/'SUBMISSION-NOTE.md').write_text(note)
save('DEPENDENCIES.json',[{'submissionId':'260b3ba0-d604-4f0d-9d55-934055d216b4','rationale':'Exact public T comparator for the sole final gate; its213 cache is not inherited by the native port.','evidence':d['parent_stream_sha256']},{'submissionId':'a4ee760a-0500-4d54-9822-4a3c56806fd5','rationale':'Direct arithmetic/code predecessor, strengthened comparisons/public140/square1408.','evidence':f"Byte-verified localbase{f['base']}, publicbe2902c2."},{'submissionId':'e3b5c51f-74e6-480a-82bf-5543fb1ba555','rationale':'Primary exact rail R1/R2/EXT2 and G6-prime native component source; no new approximation/retune/table adopted.','evidence':'88869d8cc23fb72120dd52533f3e48277e9b36e4; exact public patch and netlist hashes preserved.'}])
files={};streams={}
for prefix,directory in[('',r),('gate',gate),('search',search),('research',research),('ports',ports),('development',development)]:
 for p in directory.iterdir():
  if p.is_file()and'resource-preflight'not in p.name and p.name not in['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log']:
   name=(prefix+'/'if prefix else'')+p.name
   if p.name.endswith('ops.bin'):streams[name]=sha(p)
   else:files[name]=p
parent_receipt=ws/'breakthrough-context-lease-final-20261020/PUBLIC-SOURCE-VERIFICATION.json';files['parent/PUBLIC-SOURCE-VERIFICATION.json']=parent_receipt
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':streams,'scope':'Complete200-file final source, exact component/source provenance, all native/development checks, sole paired gate, qualified nonce/all screens, unchanged complete benchmark. No process listings/credentials; completed review JSON authoritative.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as archive:
 for n,p in sorted(files.items()):archive.add(p,arcname=n,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
