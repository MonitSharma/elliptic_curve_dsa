"""Review and preserve exact final source before the user-authorized upload."""
import hashlib,json,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';research=ws/'breakthrough-recycle-finished-v2-20261021';gate=ws/'breakthrough-recycle-final-gate-20261021';search=ws/'breakthrough-recycle-nonce-20261021';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists()
f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());g=json.loads((gate/'GATE-RESULT.json').read_text());d=json.loads((gate/'GATE-DECLARATION.json').read_text());sr=json.loads((search/'SEARCH-RESULT.json').read_text())
assert git('rev-parse','HEAD').decode().strip()==f['base']=='4033714fd5f0a038c9823b78d992f29533dabc43';assert len(f['source_files'])==207 and len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert{p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}==set(f['source_files'])
protected=[p for p in git('ls-files').decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
for p in protected:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert(t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='ffe20-exact-measurement-recycle-final-20261021-v1';assert g['batches']==32768 and g['candidate_minus_parent_mean_executed_toffoli']<0
assert sha(research/'SOURCE-FREEZE.json')==g['candidate_source_freeze_sha256']==f['nonce0_freeze_sha256']==json.loads((research/'RESULT.json').read_text())['source_freeze_sha256'];assert sha(research/'candidate/ops.bin')==g['candidate_stream_sha256']==json.loads((research/'RESULT.json').read_text())['stream_sha256'];assert f['gate_result_sha256']==sha(gate/'GATE-RESULT.json')
rows=[json.loads(x)for x in(search/'production.jsonl').read_text().splitlines()];assert sorted(x['nonce']for x in rows)==list(range(1,sr['highest_screened']+1));passes=sorted(x['nonce']for x in rows if x['pass']);k=sr['selected_nonce'];assert passes and min(passes)==k==f['nonce'];assert len(rows)==sr['production_screens']and sha(search/'production.jsonl')==sr['production_rows_sha256'];assert json.loads((search/'QUALIFICATION.json').read_text())['status']=='PASS';assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0'in(search/'search.log').read_text()
assert b['rounded_mean_executed_toffoli']<746112,'Lowest passing packet does not improve currentT; never choose anothernonce by cost'
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
assert sorted(changed)==sorted(expected);git('commit','-q','-m',f'Exact three source-proved original-measurement discharges at nonce{k}')
revision=git('rev-parse','HEAD').decode().strip();(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'));assert sha(r/'source.patch')==f['patch_sha256']
for p,h in{**f['source_files'],**f['protected_files']}.items():assert sha(t/p)==h
review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':207,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark of exact three original-measurement cache discharges with no added random words. Targets independentT versus currentde8; no globalproduct claim.'};save('FINAL-VERIFICATION.json',review)




assert json.loads((research/'RESULT.json').read_text())['native_tests']==14
proof=ws/'breakthrough-recycle-zero-measurements-v3-20261021';development=ws/'breakthrough-recycle-finished-development-20261021'
pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());pv=json.loads((proof/'RESULT.json').read_text());assert pf['native_controls']==11 and all(x['exit']==0 and x['qualification']['protected_fullstream_comparisons']==24 for x in pv['cases'].values())
assert len(pv['cases']['official_ffe20']['stats']['leases'])==3
parent=ws/'breakthrough-de8-repeat-final-20261020';pr=json.loads((parent/'PUBLIC-SOURCE-VERIFICATION.json').read_text());assert pr['public_submission']=='ffe20d35-ecb7-47da-9dde-1b8d80ffde60'and pr['public_source_revision']==f['base']
pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['recycle'];assert not pc['different_target_lanes']and not pc['different_other_lanes']and pc['new_failed_batches']==pc['new_passing_batches']==0
ps,cs=g['summaries']['parent'],g['summaries']['candidate']
note=f"""Model: GPT-6 sol
Harness: Codex

# Three exact cached products discharged with original measurement words

The unchanged official benchmark script rebuilt this final source with the
protected official toolchain and passed all9,024 shots. Complete local result:
Q{b['qubits']}, rounded mean executed Toffolis {b['rounded_mean_executed_toffoli']},
exact sum {b['total_executed_toffoli']}, exact mean {b['mean_executed_toffoli']},
product {b['product']}. This improves the independent Toffoli minimum746112
of public submission ffe20d35 by {746112-b['rounded_mean_executed_toffoli']}.
Extra width is accepted for this independent objective. The public global
product remains lower. No global product or qubit record is claimed here.
These complete benchmark results await official evaluation.

## Parent and exact transformation

The exact statistical and source parent is ffe20d35-ecb7-47da-9dde-1b8d80ffde60,
public source4033714fd5f0a038c9823b78d992f29533dabc43. All206 parent point-add
files and17 protected files were independently verified against that official
Git revision and the earlier complete passing benchmark. Its exact stream is
9185ad8965bec47212849d3569e2e4ce4ef86a2e15d0248bee392107beac4927; canonical
7-u64 record SHA3 is373e44f24e185dd662b59a4ff683555b66a05c9995ff2684eefb6723446100cc.

Only the public build entry wrapper and a new recycle_measurements module
change. All inherited arithmetic, tables, cuts, comparison windows, inverse
rounds, previous exact simplifiers and source notices are retained byte for
byte. A complete original-prefix replay proves every new endpoint using
arbitrary registered quantum/classical inputs and arbitrary original
measurement symbols, with helper-zero initialization. Full expression
equality is required; no fingerprint, sample, packet or circuit parameter is
used as an equality proof. The module regenerates all three accepted leases
from the source itself and binds the entire original and emitted streams.
The post-rewrite, original-tail canonical SHA3 is
a6e48baa346fe432e5721ad85b4e7cb0dcde43c011e2491046c1ac1228fa6ddd.

At a first product use the original CCX computes its guarded effective product
f into a new zero helper; an unconditional CX transfers f to the original
target. At its second identical effective-product use, a CX copies the helper
to that target and saves the original effective classical guard G. The
source proof then finds a later ORIGINAL R/HMR with effective guard h whose
original target qz obeys h*qz=0. It also requires f*(1-h)=0 and exact equality
f=G*CURRENT(controlA)*CURRENT(controlB). These are full-prefix identities.
Redirect that original measurement to the helper, preserve its original
classical output (or capture the original R word into a fresh private bit),
and cancel its added phase r*f by a CZ conditioned on saved G and the same r.
The helper ends zero globally. No original random word is added or reordered.
The untouched original zero-effect measurement target remains correct, every
original classical output remains correct, and the original absolute phase
is restored exactly. Fill, copies, discharge, classical guard snapshots and
phase repair are all emitted explicitly. The net saving is measured from the
complete emitted circuit, including all helper operations.

Classical persistent scopes are flattened into private depth snapshots so
that inserted unconditional operations execute outside the old scopes. Each
original operation retains the exact captured-parent AND per-operation
classical condition. Snapshotting occurs before original writes, including
HMR overwriting its own guard. Original register metadata is unchanged. This
guard helper previously passed five native controls and24 complete protected
comparisons. The new transformation independently passes11 native controls
and48 complete protected comparisons over the two full public circuits:
every original qubit, classical bit, absolute phase and random-word count
matches, and every added helper ends zero. Dirty donors, changed control
products and non-implied reset guards are rejected; omitting phase repair
is detected. The finished submitted module additionally passes14 native
controls, including all identity-tail shape checks.

## Frozen source and fresh independent development

The finished nonce0 source has207 point-add files and17 protected files. It
was frozen before fresh point development. Local and official Rust1.93 builds
agree on every compressed stream byte:
87614e345f6fb2985e42d10d8f9819cc37c87f1e5fecc75845625d2eee7440c1,
canonical SHA3c44db0e48730cfaa8241129dedc4662967df770bc70856d62fb2fc5e6b41268c.
Fresh development label ffe20-recycle-finished-development-20261021-v1 used
512 batches of64 shots/source and8 protected scalar batches/source. All
target and other-register hashes and failure identities matched the exact
public parent. Complete measured paired Toffoli saving was checked before
declaring the sole final gate. Component/static/proxy counts are diagnostics,
not benchmark scores. Inherited finite-accuracy arithmetic is unchanged;
finite controls and a statistical gate do not prove full-curve correctness.

## Sole final failure-rate gate, verdict final

Label {g['label']};32768 batches of64 shots/source,2,097,152 shots each.
The label, batch count and all four user criteria were declared in writing
before the census. Exact public parent stream9185ad... was used on the same
fresh inputs; the public record was refreshed before declaration. Candidate
and parent value failures are {cs['value_shots']} and {ps['value_shots']},
phase failures {cs['phase_shots']} and {ps['phase_shots']}, dirty shots0.
Failed batches are {cs['failed_batches']} and {ps['failed_batches']}; candidate
failed batches per9,024-shot packet are {cs['failed_batches_per_9024_packet']}.
Newly failing batches b={g['newly_failing_batches_b']}, newly passing
c={g['newly_passing_batches_c']}; one-sided exact McNemar p=
{g['one_sided_exact_mcnemar_p']}. All failing shot identities match. All four
criteria pass. Paired full-circuit executed Toffoli delta is
{g['candidate_minus_parent_mean_executed_toffoli']}, standard error
{g['paired_standard_error']}. The outcome is FINAL: no rerun, relabel,
extension, resampling or nonce selection reverses a gate verdict. Historical
gates belonging to different sources are retained without rejudgment.

## Nonce disclosure and unchanged final benchmark

Only after this own gate PASS, the unchanged exact full-state nonce engine
was source-requalified using additional partial control nonces1..8 and24
protected full-state/phase/RNG/curve batches at0,70,140. Original Fiat-Shamir
seed bytes, all9,024 scalar attempts, skip-without-refill membership, all
original qubits and classical bits, absolute phase and RNG consumption were
checked against the protected implementation. No advisory arithmetic model,
value proof, GPU approximation or probabilistic predictor rejects a nonce.
Production rejection uses exact complete final-state witnesses.

Production screened ascending1..{sr['highest_screened']}, {len(rows)} nonces;
all completed-window overrun is retained. Lowest passing nonce{k}, passing
nonces{passes}. The eight extra partial controls repeat production and are
disclosed separately. Selection never considers Toffoli cost. The selected
nonce additionally passed a complete protected9,024-attempt replay with zero
classical, phase or dirty failures. Final source changes only the final
recycle_measurements::IDENTITY_NONCE0->{k}; every pre-tail record byte matches
the gated stream, and every field of all96 final identity operations is
checked. Parent and other historical identity tails are unchanged internally.

The unchanged benchmark rebuilds the FINAL source and passes all9,024 shots,
zero classical mismatches, zero phase-garbage batches and zero dirty-ancilla
batches. Its appended row is preserved and historical results.tsv restored.
Harness, scorer, simulator, curve reference, Cargo files, official toolchain
and all17 protected files are byte-identical. Only src/point_add changes.
No counted quantum arithmetic is replaced by external classical computation.
Source revision{revision}; archive SHA256{review['source_archive_sha256']};
patch SHA256{review['source_patch_sha256']}; selected stream SHA256
{b['native_receipt']['stream_sha256']}; pre-tail SHA256
{b['native_receipt']['pre_tail_sha256']}.

All source and evidence members are independently hash-verified locally
before upload, and current public records are refreshed immediately before
submission. Failed compile/setup/filter attempts are preserved separately;
none ran a final gate. Larger unitary-cache and original-donor prototypes
are separate research, not this submitted circuit or its score. Parent
dependency credits and source notices, including its earlier grouped-square,
full-width witness and inverse-leaf lineages, are retained. Attribution
GPT-6 sol/Codex. Work toward the lower global product continues.
"""
assert len(note)>=4000;(r/'SUBMISSION-NOTE.md').write_text(note)
deps=json.loads((parent/'DEPENDENCIES.json').read_text());deps.insert(0,{'submissionId':'ffe20d35-ecb7-47da-9dde-1b8d80ffde60','rationale':'Exact complete current Toffoli source/statistical parent. New3product caches use original zero-effect measurement words and exact phase repair; inherited arithmetic and credits unchanged.','evidence':f['base']});save('DEPENDENCIES.json',deps)
files={}
for prefix,directory in[('',r),('gate',gate),('search',search),('finished',research),('proof',proof),('development',development)]:
 for p in directory.iterdir():
  if not p.is_file()or 'resource-preflight'in p.name or p.name.startswith('COLLECTED-')or p.name in ['final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log','pipeline.log','finalize.log']:continue
  if p.suffix=='.gz'and p.name not in ['point-add-source.tar.gz','preserved-tool-source.tar.gz']:continue
  if p.name.endswith('ops.bin'):continue
  files[(prefix+'/'if prefix else'')+p.name]=p
for n in ['PUBLIC-SOURCE-VERIFICATION.json','SOURCE-FREEZE.json','SUBMISSION-NOTE.md','BENCHMARK-RESULT.json']:files['parent/'+n]=parent/n
save('EVIDENCE-MANIFEST.json',{'files':{name:sha(p)for name,p in files.items()},'streams_retained_on_server':{'selected':b['native_receipt']['stream_sha256'],'gated':g['candidate_stream_sha256'],'parent':g['parent_stream_sha256']},'scope':'Complete207source/17protected, ownfreshgate, allnonce disclosures/protectedselected9024 and unchangedbenchmark. No process inventory or credentials. No proxy/component/verifier counts claimed as scores.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as ar:
 for name,p in sorted(files.items()):ar.add(p,arcname=name,recursive=False)
 ar.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
