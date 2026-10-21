"""Review and preserve exact final source before the user-authorized upload."""
import hashlib,json,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';research=ws/'breakthrough-borrowed-recycle-finished-20261021';gate=ws/'breakthrough-borrowed-recycle-final-gate-20261021';search=ws/'breakthrough-borrowed-recycle-nonce-20261021';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists()
f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());g=json.loads((gate/'GATE-RESULT.json').read_text());d=json.loads((gate/'GATE-DECLARATION.json').read_text());sr=json.loads((search/'SEARCH-RESULT.json').read_text())
assert git('rev-parse','HEAD').decode().strip()==f['base']=='4033714fd5f0a038c9823b78d992f29533dabc43';assert len(f['source_files'])==207 and len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert{p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}==set(f['source_files'])
protected=[p for p in git('ls-files').decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
for p in protected:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert(t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='cb2253-borrowed13-final-20261021-v1';assert g['batches']==32768 and g['candidate_minus_parent_mean_executed_toffoli']<0
assert sha(research/'SOURCE-FREEZE.json')==g['candidate_source_freeze_sha256']==f['nonce0_freeze_sha256']==json.loads((research/'RESULT.json').read_text())['source_freeze_sha256'];assert sha(research/'candidate/ops.bin')==g['candidate_stream_sha256']==json.loads((research/'RESULT.json').read_text())['stream_sha256'];assert f['gate_result_sha256']==sha(gate/'GATE-RESULT.json')
rows=[json.loads(x)for x in(search/'production.jsonl').read_text().splitlines()];assert sorted(x['nonce']for x in rows)==list(range(1,sr['highest_screened']+1));passes=sorted(x['nonce']for x in rows if x['pass']);k=sr['selected_nonce'];assert passes and min(passes)==k==f['nonce'];assert len(rows)==sr['production_screens']and sha(search/'production.jsonl')==sr['production_rows_sha256'];assert json.loads((search/'QUALIFICATION.json').read_text())['status']=='PASS';assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0'in(search/'search.log').read_text()
assert b['rounded_mean_executed_toffoli']<746099,'Lowest passing packet does not improve currentT; never choose anothernonce by cost'
assert b['status']=='COMPLETE_UNCHANGED_BENCHMARK_PASS'and b['tested_shots']==9024 and b['qubits']==json.loads((research/'RESULT.json').read_text())['qubits'];assert sha(t/'ops.bin')==b['native_receipt']['stream_sha256']and b['native_receipt']['pre_tail_byte_identical_to_gated_source'];assert 'all 9024 shots OK'in(r/'benchmark.log').read_text();assert b['product']==b['qubits']*b['rounded_mean_executed_toffoli']
with tarfile.open(r/'point-add-source.tar.gz')as a:
 assert{m.name for m in a.getmembers()}==set(f['source_files'])
 for p,h in f['source_files'].items():assert hashlib.sha256(a.extractfile(p).read()).hexdigest()==h
assert sha(r/'point-add-source.tar.gz')==f['source_archive_sha256']
modes={line.split('\t',1)[1]:line.split(' ',1)[0]for line in git('ls-tree','-r',f['base'],'--','src/point_add').decode().splitlines()};assert set(modes).issubset(f['source_files'])
for p in f['source_files']:modes.setdefault(p,'100644')
for p in sorted(f['source_files']):
 blob=git('hash-object','-w','--no-filters',p).decode().strip();git('update-index','--add','--cacheinfo',modes[p]+','+blob+','+p);assert git('cat-file','blob',':'+p)==(t/p).read_bytes()
changed=git('diff','--cached','--name-only').decode().splitlines();assert changed and all(p.startswith('src/point_add/')for p in changed);expected=[]
for p,h in f['source_files'].items():
 prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
 if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:expected.append(p)
assert sorted(changed)==sorted(expected);git('commit','-q','-m',f'Exact thirteen original-zero donor holds and unitary cleanup at nonce{k}')
revision=git('rev-parse','HEAD').decode().strip();(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'));assert sha(r/'source.patch')==f['patch_sha256']
for p,h in{**f['source_files'],**f['protected_files']}.items():assert sha(t/p)==h
review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':207,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark of exact thirteen original-zero donor cache holds and unitary cleanup. Targets independentT versus currentcb2253; no globalproduct claim.'};save('FINAL-VERIFICATION.json',review)





assert json.loads((research/'RESULT.json').read_text())['native_tests']==21
proof=ws/'breakthrough-borrowed-recycle-20261021';development=ws/'breakthrough-borrowed-recycle-development-20261021';pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());pv=json.loads((proof/'RESULT.json').read_text());assert pf['native_controls']==18 and all(x['exit']==0 and x['qualification']['protected_fullstream_comparisons']==24 for x in pv['cases'].values());assert pv['cases']['official_ffe20']['stats']['accepted_leases']==13 and pv['cases']['official_ffe20']['stats']['qubits']==1464
parent=ws/'breakthrough-recycle-final-20261021';pr=json.loads((parent/'PUBLIC-SOURCE-VERIFICATION.json').read_text());assert pr['public_submission']=='cb2253eb-7318-416b-8c9e-af9a28bda867'and pr['public_source_revision']=='90c5d46f8394eb584ab15b6d0bc2969a66f86b17'and pr['exact_parent_stream_sha256']==g['parent_stream_sha256']
buildparent=ws/'breakthrough-de8-repeat-final-20261020';br=json.loads((buildparent/'PUBLIC-SOURCE-VERIFICATION.json').read_text());assert br['public_source_revision']==f['base']=='4033714fd5f0a038c9823b78d992f29533dabc43'
pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['borrowed'];assert not pc['different_target_lanes']and not pc['different_other_lanes']and pc['new_failed_batches']==pc['new_passing_batches']==0
ps,cs=g['summaries']['parent'],g['summaries']['candidate']
note=f"""Model: GPT-6 sol
Harness: Codex

# Thirteen exact product holds in original zero wires, with unitary cleanup

The unchanged official benchmark script rebuilt this final source with the
protected official toolchain and passed all9,024 shots. Complete local result:
Q{b['qubits']}, rounded mean executed Toffolis {b['rounded_mean_executed_toffoli']},
exact sum {b['total_executed_toffoli']}, exact mean {b['mean_executed_toffoli']},
product {b['product']}. It beats the independent public Toffoli minimum746099
of cb2253eb by {746099-b['rounded_mean_executed_toffoli']} rounded Toffolis and
restores original width1464, three fewer qubits than that immediate statistical
parent. The global product record remains lower; no global product or minimum
qubit record is claimed. This complete local benchmark awaits official
evaluation. Nonce selection never uses cost.

## Distinguish original build lineage from current statistical parent

The actual refreshed statistical parent is cb2253eb-7318-416b-8c9e-af9a28bda867,
Q1467/T746099, official source90c5d46f8394eb584ab15b6d0bc2969a66f86b17,
stream17f8932644fb5ebf1122a9b5240ff675fd830fc7516f82e667608850c93085a8.
Its207 source files and17 protected files were independently checked against
its passing benchmark and published Git objects before this new gate.

The build lineage for this implementation is the older complete FFE source
4033714fd5f0a038c9823b78d992f29533dabc43, all206 original source files with
17 protected files, stream9185ad8965bec47212849d3569e2e4ce4ef86a2e15d0248bee392107beac4927,
canonical373e44f24e185dd662b59a4ff683555b66a05c9995ff2684eefb6723446100cc.
The frozen source was prepared before cb2253 finished publication; its historical
SOURCE-SPEC reference to FFE is build lineage, and the new gate explicitly
uses current cb2253. This is not a claim of unchanged cb2253 source. Its
three added-wire measurement discharges are replaced by13 holds on original
zero wires with exact unitary transfer. Original FFE arithmetic, cutoffs,
round counts, windows, tables, earlier exact passes and notices are unchanged.
Only the original public build entry wrapper and one new module differ from
that206-file build source, giving207 point-add files.

## Exact full-prefix product and cleanup proof

A full original-stream Boolean replay starts registered quantum/classical
inputs as arbitrary symbols, helperszero and every original measurement as
a fresh arbitrary symbol. Complete expression equality, not fingerprints,
proves identical effective guarded CCX products f at the two accepted sites.
The later original target immediately after the source CCX is also exactly f.
Since that source CCX toggles f, its target before the operation is globally
zero. No random curve input or packet nominates an equality or changes the
circuit. Unknown or unproved cases are excluded.

The first original CCX is redirected into a proven zero donor; CX copies f
to the original first target. At the last site, CX copies f to the original
zero target and CX from that target clears the donor. All operations are
explicitly emitted. The original last CCX is removed. The donor ends zero
globally, the original target has exactly its source value, and all original
absolute phases, classical values and random-word ordering are preserved.
There is no new measurement, redirected HMR, measurement phase repair or
quantum arithmetic approximation in this new module.

An independent second full original-prefix replay proves the selected physical
donor zero BEFORE first use. A precomputed inclusive[first,last] touch list
forbids EVERY original quantum read, write or phase touch to that donor,
including a zero-valued source control or a Z/CZ/CCZ. Metadata is not treated
as a quantum operation. Overlapping holds cannot use the same physical wire.
Thus the donor is an original idle zero wire during the entire hold. Its
physical ID remains within the original1464 wires; no added quantum storage
is hidden. Every source qubit is restored to its original value before its
next original use. The precise future-target and donor assertions are bound
to the complete original input and output record hashes, never transferred
as a fingerprint from another prefix.

Original persistent classical scopes are flattened using private captured
depth bits. Original operations retain their exact old snapshot AND original
per-operation guard; inserted global copies execute outside the old scopes.
Classical snapshots are made before source writes and HMR, and original
register metadata is unchanged. This guard helper has its own prior5native
and24complete protected controls. The new component has18native controls
and48complete protected comparisons on both complete public source streams:
every original quantum/classical bit, absolute phase and RNG consumption
matches, and no extra quantum wire is used. Four donor-specific controls
cover zero-lifetime use, a source touch through an original zero control,
nonzero initialization and inclusive phase/overlap constraints. Earlier
unitary tests include same-last-site ownership transfer and an omitted
cleanup fault that is detected as dirty. The final runtime module passes
21native controls including all final identity-tail validation tests.

The qualified original-tail post-borrow canonical SHA3 is
4d22fd4af8ca8044063b8438e10b744e672557a2cbc0ff2aff354d3501881609.
The finished nonce0 source207/protected17 was frozen before fresh development.
Local and official Rust1.93 generation reproduce every byte:
8d4771c7b02d5801235eef8114c5f72e64151afa078c9b0452e18a424e4547bb,
canonical71788a6496e5e07cc943adaafcfec4fd423e1b2a967e747ab912129a77bed856.
Fresh512x64/source development label
cb2253-borrowed13-development-20261021-v1 includes8protected scalar batches
per source, exact current cb2253 comparator, every target/other-register hash
and all value/phase/dirty identities. All match. Component and static proxy
counts are diagnostics, not scored results. Inherited finite-accuracy
arithmetic remains; finite tests are not universal full-curve correctness.

## Sole final fresh gate against the actual current record

Label {g['label']},32768batches of64shots/source,2,097,152shots each. Label,
batch count and allfour user criteria were declared before the census.
Current public records and exact parent source/stream were checked before
declaration. Parent/candidate value-failing shots {ps['value_shots']}/
{cs['value_shots']}, phase-failing shots {ps['phase_shots']}/{cs['phase_shots']},
dirty shots0. Failed batches {ps['failed_batches']}/{cs['failed_batches']};
candidate failed batches per9,024-shot packet
{cs['failed_batches_per_9024_packet']}. Newly failing batches b=
{g['newly_failing_batches_b']}, newly passing c={g['newly_passing_batches_c']};
one-sided exact McNemar p={g['one_sided_exact_mcnemar_p']}. All failing-shot
identities match. Allfour criteria pass. Complete paired executed-Toffoli
delta{g['candidate_minus_parent_mean_executed_toffoli']}, standard error
{g['paired_standard_error']}; this includes the complete source and all
helper operations. The verdict is FINAL: no relabel, resample, extension or
nonce changes reverse it. All older source verdicts are preserved, not reused.

## Qualified ascending nonce and final unchanged benchmark

Only after this own gate PASS, the unchanged exact full-state nonce engine
was qualified on this stream using additional partial controls1..8 and24
protected full-state/phase/RNG/curve batches at0,70,140. All9,024 original
scalar attempts, skip-without-refill membership and original Fiat-Shamir
seed/post-input random bytes are checked. Every original quantum/classical
bit and phase is checked at each selected control batch. No arithmetic
surrogate, advisory predictor, value-only model or GPU approximation rejects
a production nonce. Rejections have exact full final-state witnesses.

Ascending production1..{sr['highest_screened']}, {len(rows)} screens, all
completed-window overrun retained. Lowest passing nonce{k}, passing nonces
{passes}. Additional control nonces1..8 repeat production and are separately
disclosed;24protected control batches. No cost-based selection. The selected
nonce passes a complete protected9,024-attempt packet replay with zero
classical/phase/dirty failures. Only the final IDENTITY_NONCE0->{k} changes
from the gated source. Every pre-tail byte and every field of all96 final
identity operations is checked. Historical inner parent tails remain intact.

The unchanged benchmark rebuilds this FINAL source and passes all9,024 shots,
zero classical mismatches, zero phase-garbage and zero dirty-ancilla batches.
The appended row is saved and historical results.tsv restored. All17 protected
files, simulator, scorer, curve reference, Cargo files, official toolchain and
harness are byte-identical. Only src/point_add changes; no counted quantum
arithmetic is replaced by external classical computation. Source revision
{revision}; archive SHA256{review['source_archive_sha256']}; patch SHA256
{review['source_patch_sha256']}; selected stream
{b['native_receipt']['stream_sha256']}; pre-tail SHA256
{b['native_receipt']['pre_tail_sha256']}.

All source/evidence members are independently verified locally before upload;
fresh public checks require strict actual T improvement immediately before
submission. Other symbolic, future-target, conditional and moving-donor
experiments remain separate, never reported as this score. Failed attempts
are preserved. Full inherited dependency credits and source notices remain,
including FFE, earlier exact caches, full-width witness, shared-sum,
grouped-square and inverse-leaf work. Attribution GPT-6 sol/Codex. Research
toward a lower global product continues.
"""
assert len(note)>=4000;(r/'SUBMISSION-NOTE.md').write_text(note)
deps=json.loads((parent/'DEPENDENCIES.json').read_text());deps.insert(0,{'submissionId':'cb2253eb-7318-416b-8c9e-af9a28bda867','rationale':'Exact current Toffoli statistical comparator and complete published-source/stream baseline. Build lineage FFE retained, now13originalzero donor holds with unitary cleanup and original width.','evidence':'90c5d46f8394eb584ab15b6d0bc2969a66f86b17'});save('DEPENDENCIES.json',deps)
files={}
for prefix,directory in[('',r),('gate',gate),('search',search),('finished',research),('proof',proof),('development',development)]:
 for p in directory.iterdir():
  if not p.is_file()or 'resource-preflight'in p.name or p.name.startswith('COLLECTED-')or p.name in ['final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log','pipeline.log','finalize.log']:continue
  if p.suffix=='.gz'and p.name not in ['point-add-source.tar.gz','preserved-tool-source.tar.gz']:continue
  if p.name.endswith('ops.bin'):continue
  files[(prefix+'/'if prefix else'')+p.name]=p
for prefix,directory in [('parent',parent),('build-parent',buildparent)]:
 for n in ['PUBLIC-SOURCE-VERIFICATION.json','SOURCE-FREEZE.json','SUBMISSION-NOTE.md','BENCHMARK-RESULT.json']:files[prefix+'/'+n]=directory/n
save('EVIDENCE-MANIFEST.json',{'files':{name:sha(p)for name,p in files.items()},'streams_retained_on_server':{'selected':b['native_receipt']['stream_sha256'],'gated':g['candidate_stream_sha256'],'parent':g['parent_stream_sha256']},'scope':'Complete207source/17protected, new own gate vs currentcb2253, all qualified nonce/selected9024 and unchangedbenchmark. Source FFE lineage distinct. No proxy/component counts as scores.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as ar:
 for name,p in sorted(files.items()):ar.add(p,arcname=name,recursive=False)
 ar.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
