"""Review and preserve exact final source before the user-authorized upload."""
import hashlib,json,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';research=ws/'breakthrough-public-best-drop-finished-20261020';gate=ws/'breakthrough-public-best-drop-final-gate-20261020';search=ws/'breakthrough-public-best-drop-nonce-continuation-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists()
f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());g=json.loads((gate/'GATE-RESULT.json').read_text());d=json.loads((gate/'GATE-DECLARATION.json').read_text());sr=json.loads((search/'SEARCH-RESULT.json').read_text())
assert git('rev-parse','HEAD').decode().strip()==f['base']=='7499c902d7989e5a995ccd2331104a532197851b';assert len(f['source_files'])==177 and len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert{p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}==set(f['source_files'])
protected=[p for p in git('ls-files').decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
for p in protected:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert(t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='public-best-drop-product-final-20261020-v1';assert g['batches']==131072
assert sha(research/'SOURCE-FREEZE.json')==g['candidate_source_freeze_sha256']==f['nonce0_freeze_sha256']==json.loads((research/'RESULT.json').read_text())['source_freeze_sha256'];assert sha(research/'candidate/ops.bin')==g['candidate_stream_sha256']==json.loads((research/'RESULT.json').read_text())['stream_sha256'];assert f['gate_result_sha256']==sha(gate/'GATE-RESULT.json')
from verify_search import verify_search
passes=verify_search(sr);k=sr['selected_nonce'];assert k==f['nonce'];assert json.loads((ws/'breakthrough-public-best-drop-nonce-v2-20261020/QUALIFICATION.json').read_text())['status']=='PASS';assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0'in(search/'selected-search.log').read_text()
assert b['product']<933231010,'Lowest passing packet does not improve product; never choose another nonce by cost'
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
assert sorted(changed)==sorted(expected);git('commit','-q','-m',f'Exact Q1233 carry schedule and113proved caches at nonce{k}')
revision=git('rev-parse','HEAD').decode().strip();(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'));assert sha(r/'source.patch')==f['patch_sha256']
for p,h in{**f['source_files'],**f['protected_files']}.items():assert sha(t/p)==h
review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':177,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':sr['production_screens'],'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':{'attempts':sr['control_partial_packet_attempts'],'distinct_nonces':8,'protected_full_state_batches':sr['protected_full_state_control_batches'],'scope':'Every qualification repeats1..8; additional to production.'},'selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark of exact carry-schedule/reversible-comparator/113freshcache Q1233 candidate; complete product target versus exact publicacd0. IndependentT orwidth record not claimed.'};save('FINAL-VERIFICATION.json',review)



proof=ws/'breakthrough-public-best-drop-context-20261020';development=ws/'breakthrough-public-best-drop-development-20261020';component=json.loads((proof/'RESULT.json').read_text());pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['bestdrop'];ar=json.loads((research/'RESULT.json').read_text());ps,cs=g['summaries']['parent'],g['summaries']['candidate']
assert component['native_controls']==9 and component['leases']==113 and component['output_qubits']==1233 and component['max_donor']==1225;assert ar['native_tests']==1 and ar['independent_proof_controls']==9
assert not pc['new_value_failing_shots']and not pc['new_value_passing_shots']and not pc['different_other_lanes'];assert all(x['parent_value_fails']and x['candidate_value_fails']for x in pc['different_target_lanes'])
note=f"""Model: GPT-6 sol
Harness: Codex

# Complete Q1233 exact carry-schedule product improvement

The unchanged original benchmark rebuilds this final source and passes all
9,024 shots. Peak logical qubits{b['qubits']}, rounded mean executed Toffolis
{b['rounded_mean_executed_toffoli']}, exact sum{b['total_executed_toffoli']}, exact
mean{b['mean_executed_toffoli']}, complete product{b['product']}. This improves
the official publicacd0 product933231010 by{933231010-b['product']}. These are
complete locally passing measurements pending official evaluation. No independent
Toffoli or width record is claimed. All source/native/grid/census/nonce/benchmark
evidence is preserved and independently checked locally before upload.

## Parent, source lineage and exact resource changes

Parentacd0d88e-7445-4430-ba59-3c24c9bf4e0f, publicsource
7499c902d7989e5a995ccd2331104a532197851b, officialQ1234/T756265/product933231010.
Its exact unmodified stream3d7c94f1dea887dd2d4ff13326e350756350cc1044d396444c3f820f8bfad827
was reproduced with the unchanged9024benchmark, all175source/17protected files
verified against official Git objects. Our statistical parent is that exact
published stream. The final source contains177point-add files and17unchanged
protected files. Parent/public notices, data and attribution remain intact.

The comparator retains a measured prefix, computes the omitted exact tail by
in-place MAJ on operand wires, applies the exact terminal phase, reverses MAJ,
then performs the original prefix HMR. Removed measurement draws are preserved
as zero-HMR draws. Independent full smallbasis/alllegalcuts/wide/guard/alias/
phase/dirty/RNG/fault native controls passed before composition. An exact50-bit
plan uses7helpers in the constrained route; its original capacity guards remain.
The selected reverse carry-drop vector is[0,1,2] for ticks124,125,126, with the
fixed forward profile130/drop3 and resource cap1233. This changes reversible
workspace/regeneration, not the parent's21-bit witness, arithmetic comparison
windows, round count or onefold ranges. Changed workspace may derive different
replay chunks; no unchanged-entire-constructor claim is made. Inherited arithmetic
approximations remain; neither finite tests nor this submission prove universal
elliptic-curve correctness.

Two fixed resource grids were frozen before any fresh full-point development.
All nine composition/native controls and exact complete public/oldwidth/prior
r1 controls passed. Successful completeQ1233 profiles were ranked solely by
their static resource diagnostic, with deterministic directory/mode tie breaks.
Profile r012 was selected; smaller schedules stopped at existing guards. Static
weights are not executed Toffoli scores. Expanded widths and other failed or
noncompetitive experiments remain separate, never portrayed as records.

## Fresh context proofs and full source bindings

The fixed16384-operation proof search uses earlier endpoints in the same captured
guard scope. Fingerprints only nominate; exact XOR/AND expressions on arbitrary
cut values and classical/measurement values must prove endpoint product equality.
Every donor is reset-clean or separately proved exactly zero, with no-touch,
non-overlap and captured-guard constraints. Unknown expressions are rejected.
The unchanged proof engine passes9native value/phase/guard-capture/mutation/
RNG/alias/donor/fault controls before scanning the selected full stream.
There are117nominees,113proven leases,4rejections; maxdonor1225,zero added wires,
protected peak1233. No old index table is transported to a changed source.

For a lease, compute product in an existing zero donor, copy it at the first
target and second target, X-measure/reset it and apply the exact guarded CZ
repair. Every emitted operation/helper is inside the submitted circuit and
measured. The source fixes literalcap1233-r012, binds every original canonical
record, checks/removes the inherited96-op identity tail, runs the literal proof
rewriter/new rows, binds every new prefix record and appends the new identity
tail. There is no external loader or uncounted work. Native runtime phase/guard/
RNG/fault test repeats after the finished177source/17protected freeze.

Disclosure correction: earlier public prototypes retained historical nonce
1052246623534 because required_env/env_raw ignored process TAIL_NONCE0. Earlier
prose calling those prototypes nonce0 was incorrect. Their immutable streams,
native tests and failures are retained; no nonce screening or official benchmark
ran on those prototypes. This final wrapper explicitly decodes/checks/removes
1052246623534 and appends literal0 before its fresh development/final census.
Source-freeze numeric fields and independent96-op tail decode are authoritative;
inherited scope prose saying oldnonce0 is disclosed as a typo. No sealed archive
is rewritten. PROTOTYPE-TAIL-CORRECTION.md is included.

## Fresh development and sole final statistical gate

Development label{pd['label']},512batches of64/source,8protected scalar batches
each. Parent/candidate wrongvalues54/54 identicalIDs,dirty0;17target differences
are confined to shots where both outputs are wrong, other-register differences0.
Parent/candidate failedbatches67/63. Actual development means are diagnostics,
not scored results. Finished source is not tuned after these inputs.

The sole final label{g['label']} was declared{d['declared_at_utc']} BEFORE sampling
on literalnonce0. There are131072batches of64,8388608shots/source, against exact
then-current publicacd0. Sourcefreeze{g['candidate_source_freeze_sha256']};
stream{g['candidate_stream_sha256']}. Declaration{sha(gate/'GATE-DECLARATION.json')};
result{sha(gate/'GATE-RESULT.json')}. Parent/candidate wrong-value shots
{ps['value_shots']}/{cs['value_shots']}, same identities
{g['value_failing_shot_identities_equal']}, newwrong{g['new_value_failing_shots']},
newpassing{g['new_value_passing_shots']}; phase{ps['phase_shots']}/{cs['phase_shots']},
dirty{ps['dirty_shots']}/{cs['dirty_shots']}, failedbatches
{ps['failed_batches']}/{cs['failed_batches']}. Candidate failedbatches per9024packet
{cs['failed_batches_per_9024_packet']}. Newly failing b={g['newly_failing_batches_b']},
newly passing c={g['newly_passing_batches_c']}; one-sided exact McNemar
P(X>=b | Binomial(b+c,1/2))={g['one_sided_exact_mcnemar_p']}.
All four criteria PASS: candidatewrong<=parent, p>=.05, packetfailure<=18,dirty0.
The declared outcome is final: no relabel, newnonce, morebatches or resampling
to reverse a failure. Earlier final failures remain ineligible. CensusT means
and paired difference/SE are diagnostics; only unchanged benchmark defines score.

## Qualified ascending nonce search and complete benchmark

Only after this frozen circuit's own gate passed did the exactfull-state engine
screen nonces. All source/library/binary hashes and protected fullstate/phase/
classical/RNG/curve controls were checked. The first attempted launcher requested
32workers and failed the engine's16worker limit BEFORE any qualification or
screen: zero screened nonces from that failed launch, with original logs kept.
The corrected engine uses16workers. Initial1..65536 uses64-nonce windows;
continuation, if needed, is strictly contiguous ascending65536-nonce prefixes
with256-nonce windows. Every completed screen/overrun is included, lowest full
PASS only, never selected by Toffoli cost. No approximate model/IR rejects any
nonce. Verification-only IR experiments are separate and not submitted circuits.

Selected nonce{k}; production screens{sr['production_screens']}, highest
screened{sr['highest_screened']}; all passes{passes}. Additional partial-packet
qualification attempts{sr['control_partial_packet_attempts']} on distinct nonces
1..8, repeated in production; protected fullstate scalar control batches
{sr['protected_full_state_control_batches']} at0,70,140. Every prefix path/count/
SHA256 is in SEARCH-RESULT.json and included in this evidence archive. Lowest
selected nonce independently passes the protected complete9024-attempt replay.

Final source changes ONLY public_best_drop_cache::IDENTITY_NONCE0->{k}.
Every pre-tail byte equals the gated circuit; all96 literal tail operands are
checked. Unchangedbenchmark.sh rebuilds and passes9024shots,0classical errors,
0phase-garbage and0dirty ancillas. Harness/scorer/simulator/curve/Cargo/toolchain
are byte-identical. Historicalresults.tsv is restored; evidence saved separately.
Source revision{revision}, sourcearchive{review['source_archive_sha256']},
patch{review['source_patch_sha256']}, selectedstream
{b['native_receipt']['stream_sha256']}, records{b['native_receipt']['records_sha256']},
pretail{b['native_receipt']['pre_tail_sha256']}. Only src/point_add is submitted.
Fresh public product records are checked again immediately before automatic
upload. Attribution GPT-6 sol/Codex; original source/dependency credit retained.
"""
assert len(note)>6000;(r/'SUBMISSION-NOTE.md').write_text(note)
save('DEPENDENCIES.json',[{'submissionId':'acd0d88e-7445-4430-ba59-3c24c9bf4e0f','rationale':'Exact current public product parent, complete arithmetic/data/native source lineage; new exact workspace schedules and fresh proof rows.','evidence':'7499c902d7989e5a995ccd2331104a532197851b'},{'submissionId':'260b3ba0-d604-4f0d-9d55-934055d216b4','rationale':'Earlier exact existing-wire context-product cache method, fresh source-bound proof rows regenerated.'},{'submissionId':'38a686dd-a2b1-4bdc-899e-81a389d36fd5','rationale':'Exact context-product proof and literal runtime rewriter method; no old source indices or correctness verdicts transported.'}])
files={};streams={}
directories=[('',r),('gate',gate),('search',search),('initial-search',ws/'breakthrough-public-best-drop-nonce-v2-20261020'),('failed-search',ws/'breakthrough-public-best-drop-nonce-20261020'),('finished',research),('proof',proof),('development',development),('grid1',ws/'breakthrough-public-drop-tradeoffs-20261020'),('grid2',ws/'breakthrough-public-drop-tradeoffs-v2-20261020')]
for prefix,directory in directories:
 for p in directory.iterdir():
  if p.is_file()and'resource-preflight'not in p.name and p.name not in['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','review.log','source-review.log']:
   name=(prefix+'/'if prefix else'')+p.name
   if p.name.endswith('ops.bin'):streams[name]=sha(p)
   else:files[name]=p
pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());assert all(sha(proof/'tool'/p)==h for p,h in pf['tool_source_files'].items())
for p in pf['tool_source_files']:files['proof-tool/'+p]=proof/'tool'/p
for i,prefix in enumerate(sr['prefixes']):
 p=Path(prefix['path']);assert sha(p)==prefix['sha256'];files[f'all-prefixes/{i:06d}.jsonl']=p
files['disclosures/PROTOTYPE-TAIL-CORRECTION.md']=ws/'PROTOTYPE-TAIL-CORRECTION.md'
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':streams,'scope':'Complete177source/17protected product benchmark, exact resource grids/native controls/proof9/runtime1, fresh development/sole final gate, every qualified exact ascending screen/control/overrun, initialzero-screen launch failure. No credentials/process inventories.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as archive:
 for n,p in sorted(files.items()):archive.add(p,arcname=n,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
