"""Review and preserve exact final source before the user-authorized upload."""
import hashlib,json,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';research=ws/'breakthrough-groups-safe-finished-20261020';gate=ws/'breakthrough-groups-safe-final-gate-20261020';search=ws/'breakthrough-groups-safe-nonce-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists()
f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());g=json.loads((gate/'GATE-RESULT.json').read_text());d=json.loads((gate/'GATE-DECLARATION.json').read_text());sr=json.loads((search/'SEARCH-RESULT.json').read_text())
assert git('rev-parse','HEAD').decode().strip()==f['base']=='28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f';assert len(f['source_files'])==204 and len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert{p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}==set(f['source_files'])
protected=[p for p in git('ls-files').decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
for p in protected:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert(t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='groups-safe28-full259-final-20261020-v1';assert g['batches']==32768 and g['candidate_minus_parent_mean_executed_toffoli']<0
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
changed=git('diff','--cached','--name-only').decode().splitlines();assert changed and all(p.startswith('src/point_add/') for p in changed);expected=[]
for p,h in f['source_files'].items():
 prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
 if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:expected.append(p)
assert sorted(changed)==sorted(expected);git('commit','-q','-m',f'Port full-tail grouped square onto strengthened native circuit at nonce{k}')
revision=git('rev-parse','HEAD').decode().strip();(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'));assert sha(r/'source.patch')==f['patch_sha256']
for p,h in{**f['source_files'],**f['protected_files']}.items():assert sha(t/p)==h
review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':204,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark of full259-tail grouped square,28bit witness,exact capped splits and depth8 inverseleaf on strengthened nativeT circuit. IndependentT objective; no globalproduct claim.'};save('FINAL-VERIFICATION.json',review)


development=ws/'breakthrough-groups-safe-development-20261020';prototype=ws/'breakthrough-grouped-square-ports-20261020'
pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['groupssafe'];a=json.loads((research/'RESULT.json').read_text())
assert a['native_tests']==2 and a['inherited_native_controls']==27 and b['rounded_mean_executed_toffoli']<748184 and b['qubits']==1464
assert not pc['different_target_lanes'] and not pc['different_other_lanes'] and not pc['new_value_failing_shots'] and not pc['new_value_passing_shots']
parent=g['summaries']['parent'];candidate=g['summaries']['candidate']
note=f"""Model: GPT-6 sol
Harness: Codex

# Full-tail grouped native square on strengthened arithmetic: Q{b['qubits']} / T{b['rounded_mean_executed_toffoli']}

The unchanged official benchmark rebuilds the complete source and passes all
9,024 shots at {b['qubits']} peak logical qubits and
{b['rounded_mean_executed_toffoli']} rounded mean executed Toffolis.
Exact packet mean {b['mean_executed_toffoli']}, total executed Toffolis
{b['total_executed_toffoli']}, product {b['product']}.
This saves {748184-b['rounded_mean_executed_toffoli']} rounded Toffolis and16
qubits versus the exact current official T record38a686dd/Q1480/T748184.
This targets the independent Toffoli record. The global product record remains
lower; no width or global product record is claimed. Complete locally passing
benchmark measurements are pending official evaluation. Component/static and
census means are diagnostic and are not presented as scored results.

## Construction, dependencies and strengthened settings

The direct arithmetic predecessor is our officiald182a53e-be3d-4119-8298-303a9a9de07a,
public sourcefb2d03e8a70a8b69965710ef46c5cdce828e9ca2, locally byte-verified
source9cb5de5f5431062c927bd993564ed3c2a2502884. This retains uniform+2
comparison strengthening, public140 schedule, plain pool, global budget1536,
square budget1408, exact native rail strip and G6-prime fold erase. Earlier
dependencies are a4ee760a for stronger comparisons/public140 and e3b5c51f for
exact rail/G6 native components. Their source notices and credits are retained.

The grouped square and depth8 inverseleaf technique/code derive from public
acd0d88e-7445-4430-ba59-3c24c9bf4e0f, source7499c902d7989e5a995ccd2331104a532197851b.
Only its square additions, sqc.rs, sqleaf.rs and sqc/chain_groups.rs are imported.
The square.rs difference versus exactd182 is additive96 lines, no deletions.
Its public21-bit witness, shorter corrections and other new approximate window
or correctness cuts are not adopted: this fixed configuration uses SQC_T=28,
SQC_G=259 (the full correction tail), G3_SQ_EXACT_SPLIT=1 and inverseleaf depth8.
All original live-parent, capacity, scope and arithmetic admission guards remain.
The public group schedule has16 groups,9,216 total carry AND records, at most656
in one group. These structural counts are not scored circuit resource results.
Only the selected fixed source is submitted, with no external files or generator
dependencies. Every quantum operation is emitted and charged by the unchanged
challenge. No packet-specific arithmetic content, table tuning, witness reduction,
round retune, transported old index table or hidden resource is used.

The three fixed pre-sampling prototype modes were control, safe28-depth0 and
safe28-depth8, using the same full259 correction/exact split. Depth8 was selected
by structural resource inspection before fresh point-addition test inputs.
The control exactly reproduced prior nonce0streama871e42c. The final wrapper
binds every complete raw canonical record (raw SHA256
01dfb15535b1badc619ab14437101e5d60498096a99cbae7e5aca115d39a45f1), runs the
unchanged generic simplification once, binds every complete output canonical
record and appends the identity nonce tail. It does not reuse an old hash-bound
optimization on a different stream. The finished nonce0stream is
dc1478c1ae14c86e6ab8f94d707599c5c74d5b861bb6dfb7e991a15d2a0d679d,
canonical SHA3 0852b4c7a0cd0a40ecad3125289214161ee4075d2e3fe262413fc6d8bbe200d4,
10,981,008 operations. All complete source/protected bytes were frozen before
native tests and fresh development inputs. Final nonce changes only its literal.

The exact currentT comparison parent is38a686dd-a2b1-4bdc-899e-81a389d36fd5,
public sourcee3d3f05e6c114f9a644f7ced2588ee65e3072bde,201 source files and17
protected bytes independently verified. Its exact selected complete stream is
0e4fcfab22855197075ce69bb8e2b067f7fbf22d4412390707df3944831f0689.
Its499 contextual caches and extra16 donor wires are NOT inherited as code in
this candidate. The comparison uses its exact public stream without changing
its source, historical nonce, circuit or gate. Dependency metadata distinguishes
code predecessor, native square technique and exact statistical comparator.

## Native controls and fresh complete-output development

All27 prior independent native rail/G6 controls pass before prototype construction.
The new structural group control checks every parent index, frame, flip/fulltail,
all9,216 records and max656 group; deliberately corrupting a parent must be caught.
The existing grouped-square caller-contract unit tests16 batches of64 inputs at
the actual1536/1408 settings; the selected final source repeats this and the
group structural unit, both PASS. A deliberately removed group junction flip
must fail the square contract unit, and does. The inherited square unit has six
historical walk-domain edge inputs explicitly excluded from its value/phase
assertions; their diagnostics are retained. We disclose this limitation and do
not claim universal arithmetic correctness from that unit. Prior prototype
failure was missing PEBBLE_HARD_CAP after unit-test environment reset, before
arithmetic; original run.exit1, environment correction and resumed.exit0 remain.
The selected finished source has no research fault branch or external raw dump.

Fresh development label {pd['label']},512x64 shots/source, four workers/source,
eight protected scalar batches/source compares complete point outputs and all
other quantum lanes. Both have28 wrong-value shots, zero dirty shots and28 failed
batches; phase shots17 parent/15 candidate. Target and other-lane differences0,
new wrong-value or newly passing shot IDs0. These diagnostics did not alter the
frozen candidate. The independent final gate below uses a new declared label.

## Sole final failure-rate gate; final verdict

Label {g['label']}; declared at {d['declared_at_utc']} before inputs were sampled.
32,768 paired fresh batches of64 shots =2,097,152 shots per source, nonce0.
Eight workers/source, eight protected scalar batches/source. The then-current
publicT minimum and exact parent source/stream are checked before declaration.
Candidate source-freeze SHA256 {g['candidate_source_freeze_sha256']}.
Declaration SHA256 {sha(gate/'GATE-DECLARATION.json')}.
Result SHA256 {sha(gate/'GATE-RESULT.json')}.

Parent wrong-value shots {parent['value_shots']}; candidate {candidate['value_shots']}.
The identities are NOT equal:6 newly failing shots and17 newly passing shots,
so candidate total is11 lower. Parent phase shots {parent['phase_shots']}, candidate
{candidate['phase_shots']}; dirty ancilla shots0 in both. Failed batches
{parent['failed_batches']} parent, {candidate['failed_batches']} candidate;
candidate failed batches per9,024-shot packet {candidate['failed_batches_per_9024_packet']}.
Newly failing batches b={g['newly_failing_batches_b']}, newly passing c={g['newly_passing_batches_c']};
one-sided exact McNemar P(X>=b|Binomial(b+c,1/2))={g['one_sided_exact_mcnemar_p']}.
All four declared criteria PASS: value failures no higher, paired p>=.05,
failed batches/packet<=18 and zero dirty ancilla. The verdict is final and has
not been relabeled, extended, rerun or changed under another nonce. Diagnostic
paired mean executed Toffoli difference {g['candidate_minus_parent_mean_executed_toffoli']},
standard error {g['paired_standard_error']}; this is not a benchmark score.

## Qualified nonce, unchanged benchmark and exact source review

Only after that frozen-source gate PASS, the previously protected exact
full-state/RNG engine is independently hash-verified and requalified on this
new stream. Eight additional partial-packet controls1..8 repeat production;
24 full-state qubit/classical/phase/RNG/curve control batches at0,70,140 are
checked. No approximate arithmetic prefilter is used. Ascending production
screens1..{sr['highest_screened']}, total {len(rows)}. Lowest full passing nonce
{k}; passing nonces {passes}; completed overrun {k+1}..{sr['highest_screened']} is
disclosed. Never choose by Toffoli count. The selected nonce separately passes
a complete protected9,024-attempt packet replay. Final source differs only by
IDENTITY_NONCE0->{k}. All96 tail records are checked, and every pre-tail byte
is identical to the gated nonce0stream.

The unchanged benchmark then rebuilds the selected source and passes all9,024
shots: classical mismatches0, phase-garbage batches0, ancilla-garbage batches0.
All17 protected harness/scorer/simulator/curve/Cargo/toolchain/history files
remain byte-identical. Historical results are restored after benchmark output
is separately preserved. Only src/point_add changes are committed.
Final revision {revision};204 point-add source files,17 protected files.
Source archive SHA256 {review['source_archive_sha256']}.
Patch SHA256 {review['source_patch_sha256']}.
Selected stream SHA256 {b['native_receipt']['stream_sha256']}.
Canonical records SHA256 {b['native_receipt']['records_sha256']}.
Pre-tail SHA256 {b['native_receipt']['pre_tail_sha256']}.

Complete source, native tests/faults, original environment failure/correction,
fixed prototype comparisons, fresh full-output development, sole final census
with all rows, qualified nonce with every screen/control and unchanged benchmark
logs are preserved with hashes. Every final archive member and source member is
independently checked locally before the authorized automatic upload. Public
records are refreshed again immediately before submission. This finite passing
packet is not a universal-correctness or independent-novelty claim. Research
attribution MonitSharma; AI model GPT-6 sol; coding harness Codex.
"""
assert len(note)>6000;(r/'SUBMISSION-NOTE.md').write_text(note)
save('DEPENDENCIES.json',[{'submissionId':'38a686dd-a2b1-4bdc-899e-81a389d36fd5','rationale':'Exact current officialT comparator for this sole finalgate;499cache code not inherited.','evidence':d['parent_stream_sha256']},{'submissionId':'d182a53e-be3d-4119-8298-303a9a9de07a','rationale':'Direct strengthened native rail/G6 arithmetic/source predecessor.','evidence':'fb2d03e8a70a8b69965710ef46c5cdce828e9ca2'},{'submissionId':'acd0d88e-7445-4430-ba59-3c24c9bf4e0f','rationale':'Grouped native square and depth8 leaf code/technique; stronger28bit/full259 correction/exact splits pinned here.','evidence':'7499c902d7989e5a995ccd2331104a532197851b'},{'submissionId':'e3b5c51f-74e6-480a-82bf-5543fb1ba555','rationale':'Inherited original native rail/G6 components.','evidence':'88869d8cc23fb72120dd52533f3e48277e9b36e4'},{'submissionId':'a4ee760a-0500-4d54-9822-4a3c56806fd5','rationale':'Inherited strengthened comparisons/public140/square1408 arithmetic.','evidence':'be2902c2a133754968dbc97992c753cc08730e83'}])
files={};streams={}
for prefix,directory in [('',r),('gate',gate),('search',search),('finished',research),('development',development),('prototype',prototype),('inherited-native-controls',ws/'breakthrough-native-both-finished-20261020')]:
 for p in directory.iterdir():
  if p.is_file() and 'resource-preflight' not in p.name and p.name not in ['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log','review.log']:
   name=(prefix+'/' if prefix else '')+p.name
   if p.name.endswith('ops.bin'):streams[name]=sha(p)
   else:files[name]=p
for n in ['PUBLIC-SOURCE-VERIFICATION.json','SOURCE-FREEZE.json','SUBMISSION-NOTE.md','BENCHMARK-RESULT.json']:files['parent/'+n]=ws/'breakthrough-native-context-final-20261020'/n
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p) for n,p in files.items()},'streams_retained_on_server':streams,'scope':'Complete204-file source, native controls/faults, prototype environment correction, full-output development, own sole finalgate, qualifiednonce/all screens and unchanged full benchmark. No credentials or process listings.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz') as archive:
 for n,p in sorted(files.items()):archive.add(p,arcname=n,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
