from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];ex=root/'experiments';old=ex/'breakthrough-native-context-final-20261020';r=ex/'breakthrough-groups-safe-final-20261020'
s=(old/'seal.py').read_text();s=s[:s.index("parent=g['summaries']['parent'];")]
for a,b in {'breakthrough-native-context-finished-v3-20261020':'breakthrough-groups-safe-finished-20261020','breakthrough-native-context-final-gate-20261020':'breakthrough-groups-safe-final-gate-20261020','breakthrough-native-context-nonce-20261020':'breakthrough-groups-safe-nonce-20261020','native-context499-exact-final-20261020-v1':'groups-safe28-full259-final-20261020-v1','==201':'==204',"'source_files':201":"'source_files':204",'Cache499 independently exact contextual products on officialT748691 at nonce':'Port full-tail grouped square onto strengthened native circuit at nonce','Complete unchanged benchmark of499 independently exactcontext product leases on officialT748691;16 extra donor wires for independentT objective. Fresh public minimum checked before upload; no globalproduct claim.':'Complete unchanged benchmark of full259-tail grouped square,28bit witness,exact capped splits and depth8 inverseleaf on strengthened nativeT circuit. IndependentT objective; no globalproduct claim.'}.items():s=s.replace(a,b)
line=next(x for x in s.splitlines() if x.startswith('changed=git('))
s=s.replace(line,"changed=git('diff','--cached','--name-only').decode().splitlines();assert changed and all(p.startswith('src/point_add/') for p in changed);expected=[]\nfor p,h in f['source_files'].items():\n prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)\n if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:expected.append(p)\nassert sorted(changed)==sorted(expected);git('commit','-q','-m',f'Port full-tail grouped square onto strengthened native circuit at nonce{k}')")
s+='''
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
'''
ast.parse(s);(r/'seal.py').write_text(s);(r/'review.py').write_bytes((old/'review.py').read_bytes())
s=(old/'submit.py').read_text().replace('d182a53e-be3d-4119-8298-303a9a9de07a','38a686dd-a2b1-4bdc-899e-81a389d36fd5').replace("'source_files':201","'source_files':204");ast.parse(s);(r/'submit.py').write_text(s)
s=(ex/'../autorun-20261020-breakthrough/collect-native-context-final.py').resolve() if False else (root/'experiments/autorun-20261020-breakthrough/collect-native-context-final.py')
data=s.read_text().replace('breakthrough-native-context-final-20261020','breakthrough-groups-safe-final-20261020').replace('==201','==204').replace("'source_files':201","'source_files':204").replace('evidence,201 source','evidence,204 source');ast.parse(data);(Path(__file__).parent/'collect-groups-safe-final.py').write_text(data)
print(r)
