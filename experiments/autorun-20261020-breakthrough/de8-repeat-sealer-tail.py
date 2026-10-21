proof=ws/'breakthrough-de8-second-cache-20261020';development=ws/'breakthrough-de8-repeat-finished-development-20261020';pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['generic'];pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());proofrows=json.loads((proof/'extra0.json').read_text());assert pf['native_controls']==9 and len(proofrows['leases'])==2;assert not pc['different_target_lanes']and not pc['different_other_lanes'];assert json.loads((research/'RESULT.json').read_text())['native_tests']==8
ps,cs=g['summaries']['parent'],g['summaries']['candidate']
note=f"""Model: GPT-6 sol
Harness: Codex

# Two exact product holds followed by a second generic simplification pass

The unchanged challenge benchmark rebuilds this final source and passes all
9,024 shots: {b['qubits']} peak logical qubits, {b['rounded_mean_executed_toffoli']}
rounded mean executed Toffolis, exact sum {b['total_executed_toffoli']}, exact
mean {b['mean_executed_toffoli']}, product {b['product']}. This improves the
independent Toffoli minimum of submission de8bac6a/Q1464/T746114 by
{746114-b['rounded_mean_executed_toffoli']} rounded Toffolis. These are complete
locally passing benchmark measurements pending official evaluation. The global
product record remains lower; no global product or qubit record is claimed.

## Source lineage and exact changes

Statistical parent de8bac6a-afff-479e-b716-8cbf2dce6c73, public source
bd6672a873f85953eb7c5197e9cf46982ce19708, was reproduced from all 205 point-add
files and 17 protected files. Its exact stream is
131712cc9c79e9ffd3ac60c07d097a29b5252c03afa95c891c5ecdd603c60c2e.
This entry adds one source module and changes the public entry wrapper, keeping
all inherited arithmetic and source notices. A submission changes only
src/point_add; simulator, curve reference, scorer, Cargo files, toolchain,
harness and historical results remain byte-identical. No external gate work
or classical arithmetic replaces a counted part of the quantum circuit.

First, freshly search the complete parent stream for reusable AND products.
The fixed second-pass donor budgets 0,16,64 and lookback 16384 were declared
before fresh point inputs; all three produced the same two valid leases and
the same output with actual peak Q1464. Extra width was available for the
independent Toffoli objective, but these two holds use existing clean wires.
Of 849 nominees, only two pass the exact full-expression proof. Fingerprints
nominate candidates only; complete expression equality proves each endpoint,
with arbitrary cut data, old classical values and measurement outcomes. Unknown
cases are left out. Clean donors, lexical guard scope, no-touch lifetime and
non-overlap requirements are checked separately. Nine independent native
phase/value/captured-guard/mutation/RNG/donor/alias/fault controls pass. Their
frozen source, all outcomes and proof rows are archived.

Each hold computes one product into its clean donor, copies it at the two
target sites and ends with measurement/reset and its exact guarded CZ phase
repair. Every fill, copy, measurement and repair is present and counted in the
emitted circuit. The new module binds all 10,995,453 original canonical records
to d272df3f8bd9ca7d1e45dfcab6f87eca439ce3c36d2a0d24feae5092678e07cb,
then all 10,995,459 post-cache records to
9cd7196d0bbaedc5d5dfe19578f77920cb130d4f586da2f891d13d8d08dd45bf.
No old table is applied to a changed prefix without a complete input binding.

Second, check and remove the parent's literal 96-operation identity tail
(historical nonce229), run the existing generic exact simplification pipeline
once more and append the new literal identity tail. The generic code is
unchanged: product/affine/quadratic/truth simplification, interned witnesses,
measurement absorption, parity scan, conditional/zero passes and classical
factor passes. This repeats those existing exact methods after the new holds
have exposed their context. It is not a claim of new arithmetic primitives.
No carry/window/witness cutoff, GCD round count or rail envelope is reduced.
The strong 28-bit wrap witness, full259 corrections and full grouped tails,
exact splits, depth12 inverse leaf and inherited rail/G6 schedule remain.
Inherited approximations elsewhere remain; finite passing tests do not prove
universal full-curve correctness.

Before point development the fixed prototype is Q1464, 10,995,456 operations,
nonce0 stream9154237737f3624ead4a02a3f9d49260a27d37319c071bd98e25a654fdcd7de3,
canonical{json.loads((research/'RESULT.json').read_text())['records_sha3']}.
Static proxy counts were used only as diagnostics. The selected source has206
point-add files and17 protected files. Its only final parameter is the 48-bit
identity nonce. The frozen nonce0 source was rebuilt with official Rust1.93
and emitted every byte of the prototype stream identically before its own
fresh development and final gate. Eight final-source native tests pass:
both cache-phase/guard/fault tests, four full-width witness tests, one shared
sum test and one grouped-plan test. The earlier nine independent cache-proof
controls remain bound by source and artifact hashes.

## Development and final statistical gate

The initial fixed source has its own 512x64 development,8 full protected scalar
batches per source. Finished source then repeats fresh complete-output paired
development under label de8-repeat-finished-development-20261020-v1,512x64,
4workers,8 protected scalar batches each. Candidate minus parent executed
Toffoli mean {pc['candidate_minus_parent_raw_toffoli']} with paired standard
error {pc['paired_standard_error']}. Target and other-register hashes match;
all failures and raw logs are preserved. These census means are diagnostic,
not scored benchmark counts. No circuit, table or cutoff is tuned to a packet.

The sole final gate was declared {d['declared_at_utc']} before sampling:
label {g['label']},32768 batches of64 shots per source,2,097,152 shots each,
against the exact public parent stream above. Final outcome {g['verdict']}.
Value-failing shots candidate {cs['value_shots']}, parent {ps['value_shots']},
with identical shot IDs and zero new value-failing shots. Phase-failing shots
candidate {cs['phase_shots']}, parent {ps['phase_shots']}. Failed batches
candidate {cs['failed_batches']}, parent {ps['failed_batches']}; candidate
failed batches per9,024-shot packet {cs['failed_batches_per_9024_packet']}.
Candidate dirty-ancilla shots {cs['dirty_shots']}. Discordant newly failing
batches b={g['newly_failing_batches_b']}, newly passing c={g['newly_passing_batches_c']};
one-sided exact McNemar p={g['one_sided_exact_mcnemar_p']}, exceeding0.05.
All four user criteria pass. The paired executed-Toffoli saving
{-g['candidate_minus_parent_mean_executed_toffoli']} with standard error
{g['paired_standard_error']} is diagnostic. The verdict is FINAL: no rerun,
relabel, extension or another nonce is used to reverse a failure. Older gates
belong to other sources and are not reused or rejudged here.

## Qualified ascending nonce and unchanged benchmark

Only after finalPASS, the exact existing full-state search engine is requalified
on this stream: eight additional partial controls1..8,24 full protected state,
phase,RNG and curve batches at0,70,140. No arithmetic predictor, value-IR model,
symbolic proof experiment or GPU approximation rejects a production nonce.
The original full-state source-qualified simulation is the rejection test.

Production screens ascending1..{sr['highest_screened']}, {len(rows)} nonces.
The lowest complete passing nonce is{k}; all passing nonces {passes}, including
completed-window overrun after{k} through{sr['highest_screened']}, are retained.
Selection never uses Toffoli cost. The selected nonce also passes the protected
complete9,024-attempt packet replay. The final source changes ONLY
repeat_generic_cache::IDENTITY_NONCE0->{k}. Every pre-tail byte equals the
gated circuit, and every operand of all96 final tail records is checked.

Unchanged benchmark.sh rebuilds with the official toolchain and passes all9,024
shots with zero classical mismatches, zero phase-garbage batches and zero dirty
ancilla batches. The appended benchmark row is saved and historical results.tsv
is restored exactly. Source revision{revision}; source archiveSHA256
{review['source_archive_sha256']}; patchSHA256{review['source_patch_sha256']};
selected stream{b['native_receipt']['stream_sha256']}; canonical recordsSHA256
{b['native_receipt']['records_sha256']}; pre-tailSHA256
{b['native_receipt']['pre_tail_sha256']}.

All final source and evidence members are independently hash-verified locally
before upload. Public records are refreshed immediately before submission.
Earlier setup failures involving Windows text/binary patch assembly are kept
as failures; neither ran a gate or nonce search. Broader symbolic verifier
research remains separate and makes no quantum resource claim. Original
dependency credits and source notices are retained, including the full-width
polynomial/shared-sum and grouped-square lineages already disclosed by de8bac6a.
Attribution GPT-6 sol/Codex. Research toward a lower global product continues.
"""
assert len(note)>6000;(r/'SUBMISSION-NOTE.md').write_text(note)
deps=json.loads((ws/'breakthrough-exact-witness-final-20261020/DEPENDENCIES.json').read_text());deps.insert(0,{'submissionId':'de8bac6a-afff-479e-b716-8cbf2dce6c73','rationale':'Exact current Toffoli parent, complete unchanged source/stream baseline. Two fresh context-proved existing-wire holds and repeated unchanged generic pass; arithmetic and inherited credits preserved.','evidence':'bd6672a873f85953eb7c5197e9cf46982ce19708'});save('DEPENDENCIES.json',deps)
files={};streams={}
for prefix,directory in[('',r),('gate',gate),('search',search),('finished',research),('proof',proof),('development',development),('prototype',ws/'breakthrough-de8-generic-repeat-v3-20261020'),('prototype-development',ws/'breakthrough-de8-generic-development-20261020')]:
 for path in directory.iterdir():
  if path.is_file()and'resource-preflight'not in path.name and path.name not in['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log','review.log']:
   name=(prefix+'/'if prefix else'')+path.name
   if path.name.endswith('ops.bin'):streams[name]=sha(path)
   else:files[name]=path
for name in ['PUBLIC-SOURCE-VERIFICATION.json','SOURCE-FREEZE.json','SUBMISSION-NOTE.md','BENCHMARK-RESULT.json','PACKAGE-RESULT.json']:files['parent/'+name]=ws/'breakthrough-exact-witness-final-20261020'/name
save('EVIDENCE-MANIFEST.json',{'files':{name:sha(path)for name,path in files.items()},'streams_retained_on_server':streams,'scope':'Complete206source/17protected fixed two-cache/repeated-generic final evidence, fresh development, sole finalgate, qualified allnonce/protected9024, unchangedbenchmark. No process inventory or credentials; component/proxy/verifier studies are not scores.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as archive:
 for name,path in sorted(files.items()):archive.add(path,arcname=name,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
