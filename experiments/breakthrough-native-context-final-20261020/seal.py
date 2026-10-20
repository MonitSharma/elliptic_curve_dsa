"""Review and preserve exact final source before the user-authorized upload."""
import hashlib,json,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';research=ws/'breakthrough-native-context-finished-v3-20261020';gate=ws/'breakthrough-native-context-final-gate-20261020';search=ws/'breakthrough-native-context-nonce-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists()
f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());g=json.loads((gate/'GATE-RESULT.json').read_text());d=json.loads((gate/'GATE-DECLARATION.json').read_text());sr=json.loads((search/'SEARCH-RESULT.json').read_text())
assert git('rev-parse','HEAD').decode().strip()==f['base']=='28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f';assert len(f['source_files'])==201 and len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert{p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}==set(f['source_files'])
protected=[p for p in git('ls-files').decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
for p in protected:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert(t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='native-context499-exact-final-20261020-v1';assert g['batches']==32768 and g['candidate_minus_parent_mean_executed_toffoli']<0
assert sha(research/'SOURCE-FREEZE.json')==g['candidate_source_freeze_sha256']==f['nonce0_freeze_sha256']==json.loads((research/'RESULT.json').read_text())['source_freeze_sha256'];assert sha(research/'candidate/ops.bin')==g['candidate_stream_sha256']==json.loads((research/'RESULT.json').read_text())['stream_sha256'];assert f['gate_result_sha256']==sha(gate/'GATE-RESULT.json')
rows=[json.loads(x)for x in(search/'production.jsonl').read_text().splitlines()];assert sorted(x['nonce']for x in rows)==list(range(1,sr['highest_screened']+1));passes=sorted(x['nonce']for x in rows if x['pass']);k=sr['selected_nonce'];assert passes and min(passes)==k==f['nonce'];assert len(rows)==sr['production_screens']and sha(search/'production.jsonl')==sr['production_rows_sha256'];assert json.loads((search/'QUALIFICATION.json').read_text())['status']=='PASS';assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0'in(search/'search.log').read_text()
assert b['status']=='COMPLETE_UNCHANGED_BENCHMARK_PASS'and b['tested_shots']==9024 and b['qubits']==json.loads((research/'RESULT.json').read_text())['qubits'];assert sha(t/'ops.bin')==b['native_receipt']['stream_sha256']and b['native_receipt']['pre_tail_byte_identical_to_gated_source'];assert 'all 9024 shots OK'in(r/'benchmark.log').read_text();assert b['product']==b['qubits']*b['rounded_mean_executed_toffoli']
with tarfile.open(r/'point-add-source.tar.gz')as a:
 assert{m.name for m in a.getmembers()}==set(f['source_files'])
 for p,h in f['source_files'].items():assert hashlib.sha256(a.extractfile(p).read()).hexdigest()==h
assert sha(r/'point-add-source.tar.gz')==f['source_archive_sha256']
modes={line.split('\t',1)[1]:line.split(' ',1)[0]for line in git('ls-tree','-r',f['base'],'--','src/point_add').decode().splitlines()};assert set(modes).issubset(f['source_files'])
for p in f['source_files']:modes.setdefault(p,'100644')
for p in sorted(f['source_files']):
 blob=git('hash-object','-w','--no-filters',p).decode().strip();git('update-index','--add','--cacheinfo',modes[p]+','+blob+','+p);assert git('cat-file','blob',':'+p)==(t/p).read_bytes()
changed=git('diff','--cached','--name-only').decode().splitlines();assert changed==['src/point_add/exact_native_port.rs','src/point_add/leapfrog.rs','src/point_add/mod.rs','src/point_add/native_both_finished.rs','src/point_add/native_context_cache.rs','src/point_add/strip_barrel.rs','src/point_add/strip_small.rs','src/point_add/y15_onefold.rs'];git('commit','-q','-m',f'Cache499 independently exact contextual products on officialT748691 at nonce{k}')
revision=git('rev-parse','HEAD').decode().strip();(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'));assert sha(r/'source.patch')==f['patch_sha256']
for p,h in{**f['source_files'],**f['protected_files']}.items():assert sha(t/p)==h
review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':201,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark of499 independently exactcontext product leases on officialT748691;16 extra donor wires for independentT objective. Fresh public minimum checked before upload; no globalproduct claim.'};save('FINAL-VERIFICATION.json',review)

parent=g['summaries']['parent'];candidate=g['summaries']['candidate'];proof=ws/'breakthrough-native-both-context16-20261020';development=ws/'breakthrough-native-context-development-20261020';component=json.loads((proof/'RESULT.json').read_text());pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['context499'];assert component['native_controls']==7 and component['leases']==499 and component['output_qubits']==1480 and component['max_donor']==1479;assert not pc['different_target_lanes']and not pc['different_other_lanes']and not pc['new_value_failing_shots']and not pc['new_value_passing_shots'];assert json.loads((research/'RESULT.json').read_text())['native_tests']==1;assert b['rounded_mean_executed_toffoli']<748691
note=f"""Model: GPT-6 sol
Harness: Codex

# 499 independently proved context-product caches: Q{b['qubits']} / T{b['rounded_mean_executed_toffoli']}

The complete unchanged challenge benchmark rebuilds this frozen source and
passes all9,024 shots at **{b['qubits']} logical qubits and
{b['rounded_mean_executed_toffoli']} rounded mean executed Toffolis**.
Exact packet mean {b['mean_executed_toffoli']}; total executed Toffolis
{b['total_executed_toffoli']}; product {b['product']}.
The exact official T parentd182a53e/Q1464/T748691 is improved by
{748691-b['rounded_mean_executed_toffoli']} rounded Toffolis, at16 extra qubits.
This targets the independent Toffoli minimum. The global product record is
lower; no global product or width record is claimed. The public T minimum is
refreshed immediately before upload, and the selected nonce is never chosen by
its Toffoli count. These are complete locally passing benchmark measurements,
pending official evaluation, not component counts.

## Construction and source lineage

The direct arithmetic and exact-public comparator is official
d182a53e-be3d-4119-8298-303a9a9de07a, public source
fb2d03e8a70a8b69965710ef46c5cdce828e9ca2, byte-verified local source
9cb5de5f5431062c927bd993564ed3c2a2502884. Its complete stream is
cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536.
All200 parent point-add files and17 protected files were verified against the
official Git objects before the new final gate. The entire parent constructor
and all previous source-bound optimizations remain unchanged, except renaming
its entrypoint to call the new wrapper. It retains strengthened uniform+2
comparisons, public140 schedule, plain pool, square1408 workspace, global1536
budget, native rail strip and G6-prime fold erase. No new approximation,
shorter window, new table cut, smaller witness or round retune is adopted.

The context-cache technique follows our earlier official260b3ba0 and the
independent context proof engine, regenerated on this exact newer native
source. No old cache-index table, packet or statistical verdict is reused.
The fixed16,384-operation earlier-cut proof scan nominates2031 pairs, proves499
and rejects1532. Fingerprints nominate pairs only: full exact Boolean XOR/AND
expressions, with arbitrary quantum/classical cut values and measurement
outcomes, must prove equality of the effective endpoint products. The cut
never crosses the enclosing lexical guard. Each donor is independently proved
clean, untouched across its interval, and nonoverlapping with other holds.
The selected16 additional donor wires are1464..1479 where needed. Some holds
use existing wires. The complete protected analyzer measuresQ1480.

At the first endpoint the product is computed once into the donor and copied
to the original target. At the second endpoint it is copied again, the donor
is X-measured, and the matching CZ phase correction erases it exactly. The
guarded form retains captured outer guards and each per-operation condition.
Every saved native Toffoli and every added phase repair is represented in the
emitted circuit. There is no external loader, semantic hash shortcut, hidden
packet selection or uncounted quantum operation. A full canonical record
binding checks the ENTIRE official parent output before its checked historical
nonce95 identity tail is removed; another full binding checks every new cache
output record against the independent proof emitter. A new fixednonce0 tail
is appended. No additional generic simplification pass is run.

Seven independent native controls cover full-basis value/phase preservation,
guard capture and mutation, unknown per-op conditions, arbitrary prepared
aliases, rejected broken aliases, forbidden scope crossing and missing phase
repair detection. The submission's literal cache rewriter is also replayed in
its own full-basis guarded/cleanup/cost/phase-fault control. The parent's27
previously verified exact native controls and all their source bytes are
unchanged. All code, patches, tests, failed assembly attempts, logs and stream
hashes are preserved. A copied zero-added-wire prose string in the component
freeze is explicitly corrected by SCOPE-CORRECTION.json: the numeric driver and
freeze declare16 extra donors throughout. No source or run was altered by that
prose correction. The two preliminary assemblers stopped before compilation;
their original outcomes remain, and the finished V3 source is newly frozen.

The native arithmetic retains inherited approximations in its point-addition
lineage. Exact component proofs are not a claim of universal whole-circuit
correctness. Our own final statistical gate below is mandatory and all four
criteria pass. Direct ancestor attribution remains: a4ee760a/sourcebe2902c2
for the strengthened arithmetic, e3b5c51f/source88869d8c for the exact native
rail/G6 pieces, and260b3ba0/sourceaf60c815 for the earlier-context cache method.
Original source comments, notices and attributions are preserved byte-for-byte.

## Fresh full-output development

The source and all499 cache rows were frozen before a single predeclared
512x64 fresh-input comparison, labelnative-context499-development-20261020-v1,
against the exact publicd182 stream. Four workers per source; eight batches
also replayed in the unchanged protected scalar simulator. Parent/candidate
wrong-value shots: {pd['summaries']['publicd182']['value_shots']} /
{pd['summaries']['context499']['value_shots']}; dirty shots0/0. Full output
target-lane differences0, other-ancilla differences0, newly wrong-value IDs0,
newly passing value IDs0. All full hashes and individual failures are retained.
These development means are diagnostic and are not benchmark records or a
substitute for the separate final gate. Circuit choices are not fitted to
these inputs or to any challenge packet.

## Sole declared final failure-rate gate

Exact comparator: officiald182a53e/Q1464/T748691, sourcefb2d03e8. Declared at
{d['declared_at_utc']}, label**{g['label']}**,32768 batches of64 shots =
2,097,152 fresh shots per source, candidatefixednonce0. Both sources receive the
same fresh inputs. Eight census workers/source; eight batches/source are also
checked by the unchanged protected scalar simulator.

| Measurement | Parent | Candidate |
|---|---:|---:|
| Wrong-value shots | {parent['value_shots']} | {candidate['value_shots']} |
| Phase-failing shots | {parent['phase_shots']} | {candidate['phase_shots']} |
| Dirty-ancilla shots | {parent['dirty_shots']} | {candidate['dirty_shots']} |
| Failed batches | {parent['failed_batches']} | {candidate['failed_batches']} |
| Failed batches per9,024-shot packet | {parent['failed_batches_per_9024_packet']} | {candidate['failed_batches_per_9024_packet']} |
| Mean executed Toffolis | {parent['mean_executed_toffoli']} | {candidate['mean_executed_toffoli']} |

Newly failing batches b={g['newly_failing_batches_b']}; newly passing
c={g['newly_passing_batches_c']}; one-sided exact McNemar
p={g['one_sided_exact_mcnemar_p']}. Wrong-value shot identities equal:
{g['value_failing_shot_identities_equal']}; new value failures
{g['new_value_failing_shots']}, newly passing{g['new_value_passing_shots']}.
Paired candidate-minus-parent executedToffoli mean
{g['candidate_minus_parent_mean_executed_toffoli']}, standard error
{g['paired_standard_error']}.
All four gates pass: candidate value count no greater, paired p>=0.05,
failed batches per141<=18, zero dirty shots. This fixed source has one declared
final gate, whose verdict is final. No resampling, new label, extended sample
or different nonce reversed a failure. Historical failed verdicts remain.
No parent/development/other-circuit gate is reused.

Declaration SHA256{review['gate_declaration_sha256']}.
Gate result SHA256{review['gate_result_sha256']}.
Exact parent stream{g['parent_stream_sha256']}.
Candidate nonce0 stream{g['candidate_stream_sha256']}.

## Qualified ascending nonce and unchanged benchmark

Only after gatePASS, the exact frozen source independently qualifies the
generic exact full-state engine: eight additional partial-packet controls1..8
repeat production, with24 protected full qubit/classical/phase/RNG/curve states
at batches0,70,140. No approximate arithmetic filter is used. Production
screens ascending1..{sr['highest_screened']}, {len(rows)} screens total.
Lowest full passing nonce**{k}**; passing nonces{passes}. Completed overrun
{k+1}..{sr['highest_screened']} is disclosed. No cost-based nonce selection.
The selected nonce separately passes a complete protected9,024-attempt replay.
Final source differs from the gated source only by its nonce literal.

The unchanged official benchmark then performs the selected-source rebuild
and passes all9,024 shots:0 classical mismatches,0 phase-garbage batches,
0 ancilla-garbage batches. Every pre-tail byte is compared to the gated source;
all96 identity-tail records match the selected nonce. Historical results and
all17 protected harness/scorer/simulator/curve/Cargo/toolchain files are restored
and byte-identical. Onlysrc/point_add changes are committed for submission.

Final source revision{revision};201 point-add source files,17 protected files.
Source archive SHA256{review['source_archive_sha256']}.
Patch SHA256{review['source_patch_sha256']}.
Selected stream SHA256{b['native_receipt']['stream_sha256']}.
Canonical records SHA256{b['native_receipt']['records_sha256']}.
Pre-tail SHA256{b['native_receipt']['pre_tail_sha256']}.

Complete source, independent proof source, native controls/faults, full-output
development, declared census and all rows, qualified nonce and all screens,
complete benchmark and source/evidence hashes are preserved. Every archive
member and source member is checked independently on the local machine before
the authorized upload. This finite passing packet is not a universal-correctness
or independent-novelty claim. Research attribution MonitSharma; modelGPT-6 sol;
coding harnessCodex. Every direct code/technique/comparator dependency is listed.
"""
assert len(note)>6000;(r/'SUBMISSION-NOTE.md').write_text(note)
save('DEPENDENCIES.json',[{'submissionId':'d182a53e-be3d-4119-8298-303a9a9de07a','rationale':'Direct complete arithmetic/source predecessor and exact currentT comparator for this sole finalgate.','evidence':d['parent_stream_sha256']},{'submissionId':'260b3ba0-d604-4f0d-9d55-934055d216b4','rationale':'Earlier-context exactproduct-cache technique predecessor;499 rows regenerated independently, no oldindices/nonce/gate reused.','evidence':'af60c815cf7fcb927466450864cd30b03483c74c'},{'submissionId':'a4ee760a-0500-4d54-9822-4a3c56806fd5','rationale':'Inherited stronger comparisons/public140/square1408 arithmetic.','evidence':'be2902c2a133754968dbc97992c753cc08730e83'},{'submissionId':'e3b5c51f-74e6-480a-82bf-5543fb1ba555','rationale':'Inherited primary exact rail andG6 native components, without its new approximate windows or square.','evidence':'88869d8cc23fb72120dd52533f3e48277e9b36e4'}])
files={};streams={}
directories=[('',r),('gate',gate),('search',search),('finished',research),('proof',proof),('development',development),('inherited-native-controls',ws/'breakthrough-native-both-finished-20261020'),('assembly-v1',ws/'breakthrough-native-context-finished-20261020'),('assembly-v2',ws/'breakthrough-native-context-finished-v2-20261020')]
for prefix,directory in directories:
 for path in directory.iterdir():
  if path.is_file()and'resource-preflight'not in path.name and path.name not in['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log']:
   name=(prefix+'/'if prefix else'')+path.name
   if path.name.endswith('ops.bin'):streams[name]=sha(path)
   else:files[name]=path
pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());assert all(sha(proof/'tool'/p)==h for p,h in pf['tool_source_files'].items())
for p in pf['tool_source_files']:files['proof-tool/'+p]=proof/'tool'/p
for name in['PUBLIC-SOURCE-VERIFICATION.json','SOURCE-FREEZE.json','SUBMISSION-NOTE.md','BENCHMARK-RESULT.json']:files['parent/'+name]=ws/'breakthrough-native-both-final-20261020'/name
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':streams,'scope':'Complete201-file finalsource, exactcontextproofs/native/fault checks, own development/solefinalgate, independently qualifiednonce/all screens, unchangedcompletebenchmark. No process listings/credentials. Original assembly failures and scope prose correction retained.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as archive:
 for n,p in sorted(files.items()):archive.add(p,arcname=n,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
