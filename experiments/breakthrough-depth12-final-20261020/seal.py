"""Review and preserve exact final source before the user-authorized upload."""
import hashlib,json,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';research=ws/'breakthrough-depth12-finished-20261020';gate=ws/'breakthrough-depth12-final-gate-20261020';search=ws/'breakthrough-depth12-nonce-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists()
f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());g=json.loads((gate/'GATE-RESULT.json').read_text());d=json.loads((gate/'GATE-DECLARATION.json').read_text());sr=json.loads((search/'SEARCH-RESULT.json').read_text())
assert git('rev-parse','HEAD').decode().strip()==f['base']=='28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f';assert len(f['source_files'])==205 and len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert{p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}==set(f['source_files'])
protected=[p for p in git('ls-files').decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
for p in protected:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert(t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='depth12-context-final-20261020-v1';assert g['batches']==32768 and g['candidate_minus_parent_mean_executed_toffoli']<0
assert sha(research/'SOURCE-FREEZE.json')==g['candidate_source_freeze_sha256']==f['nonce0_freeze_sha256']==json.loads((research/'RESULT.json').read_text())['source_freeze_sha256'];assert sha(research/'candidate/ops.bin')==g['candidate_stream_sha256']==json.loads((research/'RESULT.json').read_text())['stream_sha256'];assert f['gate_result_sha256']==sha(gate/'GATE-RESULT.json')
rows=[json.loads(x)for x in(search/'production.jsonl').read_text().splitlines()];assert sorted(x['nonce']for x in rows)==list(range(1,sr['highest_screened']+1));passes=sorted(x['nonce']for x in rows if x['pass']);k=sr['selected_nonce'];assert passes and min(passes)==k==f['nonce'];assert len(rows)==sr['production_screens']and sha(search/'production.jsonl')==sr['production_rows_sha256'];assert json.loads((search/'QUALIFICATION.json').read_text())['status']=='PASS';assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0'in(search/'search.log').read_text()
assert b['rounded_mean_executed_toffoli']<747226,'Lowest passing packet does not improve currentT; never choose anothernonce by cost'
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
assert sorted(changed)==sorted(expected);git('commit','-q','-m',f'Exactdepth12 square andfreshly proved230 contextcaches at nonce{k}')
revision=git('rev-parse','HEAD').decode().strip();(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'));assert sha(r/'source.patch')==f['patch_sha256']
for p,h in{**f['source_files'],**f['protected_files']}.items():assert sha(t/p)==h
review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':205,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete unchanged benchmark of exactdepth12 plus freshly proved230existing-wire caches on strong grouped arithmetic; Q1464. Targets independentT versus current71, no globalproduct claim.'};save('FINAL-VERIFICATION.json',review)



proof=ws/'breakthrough-depth12-context-20261020';development=ws/'breakthrough-depth12-development-20261020';grid=ws/'breakthrough-grouped-exact-resource-grid-v2-20261020';griddev=ws/'breakthrough-grouped-resource-development-20261020';component=json.loads((proof/'RESULT.json').read_text());pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['depth12'];ar=json.loads((research/'RESULT.json').read_text());ps,cs=g['summaries']['parent'],g['summaries']['candidate'];assert component['native_controls']==9 and component['leases']==230 and component['output_qubits']==1464 and component['max_donor']==1460;assert ar['native_tests']==2 and ar['independent_proof_controls']==9;assert not pc['different_target_lanes']and not pc['different_other_lanes'];assert json.loads((grid/'RESULT.json').read_text())['native_controls']==34
note=f"""Model: GPT-6 sol
Harness: Codex

# Exact depth12 inverse-leaf conditioning plus new context proofs: Q{b['qubits']} / T{b['rounded_mean_executed_toffoli']}

The unchanged original challenge benchmark rebuilds the final frozen source and
passes all9,024 shots: Q{b['qubits']}, rounded mean executed Toffolis
{b['rounded_mean_executed_toffoli']}, exact sum{b['total_executed_toffoli']}, exact
mean{b['mean_executed_toffoli']}, product{b['product']}. The roundedT improvement
versus official71d9dc7e/Q1464/T747226 is {747226-b['rounded_mean_executed_toffoli']}
at the same width. These are complete locally passing benchmark measurements,
pending official evaluation. This targets the independentT objective. The
globalproduct record is lower; no globalproduct/width record is claimed.

## Source lineage and the actual change

The exact current statistical parent is submission71d9dc7e-550b-480d-8d9e-
c2af1989c0d7, source28a4e93e8cc020282b36413b27edce3cf0ff3ce8, selected complete
stream278802f0728d9233297723c88dffef8544bd9c3ce9968d34a2c3f406b383688a.
All205public point-add files and17protected files were previously compared to
official Git objects and its exact original benchmark was reproduced. The
final census uses that exact stream, not an older report or private proxy.

Our constructor is assembled from the independently frozen strong grouped-square
prototype derived from official8d0fef2b/source d289ee2b, with native rail/G6 from
d182a53e/e3b5c51f and public grouped-square/leaf code from acd0d88e/source7499c902.
Its depth8 control reproduces the complete precache dc1478c1 stream byte-for-byte;
the earlier native control reproduces a871e42c. We do not claim the entire71
constructor is unchanged. The exact inverse-leaf conditioning depth changes8->12,
then every context-cache row is freshly proved on the new complete stream.
The strong public140 schedule, uniform+2 comparisons, plainpool, global1536/
square1408,28-bit wrap witness, full259-bit correction tails and exact square
splits remain. No arithmetic comparison window, witness precision, cut or round
is lowered. Inherited approximations elsewhere remain and are disclosed.

The depth parameter controls an exact schedule of carry computation, early
X-measurement and matching phase-twin operations. It is not an approximate bit
window. Native production arithmetic comes from the public leaf implementation;
its original notices and credits remain. Context caching follows our prior71,
38a686dd and260b3ba0 methodology, with new source-bound proofs and new positions.
No old index table, correctness verdict, nonce or packet is transported. No
novelty or universal full-curve correctness claim is made.

## Fixed architecture research and native controls

Before any fresh full-point development the fixed grid compared depth8/12/16,
squarebudget1536 and walkbudget1664, keeping strong arithmetic parameters fixed.
Twenty-seven inherited exact controls, grouped-plan shape/parent/frame/flip
control and six leaf forward/inverse roundtrips at depths8/12/16 and widths32/64
(4,096shots each) pass:34 native controls. Every new fullsquare caller contract
also passes; its six historical walk-domain edge exclusions and raw diagnostics
are retained. These finite native tests are not a universal arbitraryfield proof.
The separate deliberate grouped-junction fault produces122 wrong values and43
phase errors in128shots and is detected. Two earlier setup attempts omitted an
independent cap setting and stopped before their intended simulations; original
failure logs/markers are preserved. The corrected version adds the missing cap
only to cfg(test) fixture setup and repeats the frozen controls; no statistical
gate was rerun. The final source removes the research fault path and raw dump.

Fresh architecture development labelgrouped-resource-grid-development-20261020-v1,
512x64 per source, fourworkers/eightprotectedscalarbatches each, compares all
fixed successful streams against exact71. Every target/other register and
wrong-value identity matches; dirty0. Depth12 mean executedT is747445.904 versus
precachedepth8 747451.782 on that development sample. Depth16 has no additional
measured benefit; larger square/walk budgets emit identical depth8 streams.
Static guard-depth weights are diagnostics and can misprice OR-of-measurement
guards; they are never presented as scoredT. Exactdepth12 is selected before
its own final source, final gate and nonce inputs.

## New exact cache proof and full canonical bindings

One fixed zero-added-wire scan uses16,384-operation earlier cuts within the SAME
lexical captured guard scope on the new depth12 fullstream f8c83372. Nine native
value/phase/guard-capture/mutation/RNG/alias/zero-donor/fault controls pass first.
Fingerprints only nominate: exact Boolean XOR/AND expressions on arbitrary cut
values and measurement/classical values must prove equality of effective
endpoint products. The donor must be reset-clean or separately proved exactly
zero; no-touch intervals, no overlapping holds and scope constraints are checked.
Unknown expressions are rejected. The scan nominates{component['proposed']},
proves{component['leases']} and rejects{component['proposed']-component['leases']}.
All donors already exist; maximum donor1460 and protected peak remains1464.

At the first endpoint the product is computed once in the zero donor and copied
to the original target; at the second it is copied, X-measured and cleared with
the exact matching guarded CZ repair. Every emitted gate and helper is counted.
The final source fixes literaldepth12 mode and binds EVERY raw operation before
running the unchanged generic pipeline once, then binds EVERY generic output
prefix. It reconstructs the checked prototype identity tail, binds EVERY complete
input record to the independently proved cache input, checks/removes that tail,
runs the literal proof rewriter/new230 rows, binds EVERY output prefix and
appends a new literal nonce0 tail. It has no external loader or uncounted work.
Research fault and raw-dump paths are removed. Source/protected byte checks,
native cache phase/guard/fault test plus grouped structural test repeat after
the final205-source/17protected freeze. Complete generation reproduces the bound
stream and protectedQ. No old cache rows are carried to changed stream indices.

## Fresh finished-source development and sole final gate

Finished-source development label{pd['label']},512x64 per source, fourworkers/
eightprotectedscalarbatches each, records all output/value/phase/dirty outcomes.
Parent values{pd['summaries']['public71']['value_shots']}, candidate values
{pd['summaries']['depth12']['value_shots']}; target/other differences0, no new
wrong-value or passing identities, dirty0. Candidate is not altered afterward.
The independent finalgate uses exact then-current official71 stream and fresh
shared inputs. Any inherited development scope prose is subordinate to the
recorded exact parent IDs, paths, source freezes and stream hashes.

Label{g['label']}, declared{d['declared_at_utc']} BEFORE sampling on nonce0.
32,768batches x64 =2,097,152shots/source, eightworkers/eightprotectedscalarbatches
each. CandidateSF{g['candidate_source_freeze_sha256']}.
DeclarationSHA256{sha(gate/'GATE-DECLARATION.json')}.
ResultSHA256{sha(gate/'GATE-RESULT.json')}.
Parent wrong-value shots{ps['value_shots']}, candidate{cs['value_shots']}; new
wrong-value shots{g['new_value_failing_shots']}, new passing{g['new_value_passing_shots']},
same identities{g['value_failing_shot_identities_equal']}. Parent/candidate phase
shots{ps['phase_shots']}/{cs['phase_shots']}, dirty{ps['dirty_shots']}/{cs['dirty_shots']}.
Failed batches{ps['failed_batches']}/{cs['failed_batches']}; candidate failed
batches per9,024-shot packet{cs['failed_batches_per_9024_packet']}.
Discordant newly failing b={g['newly_failing_batches_b']}, newly passing
c={g['newly_passing_batches_c']}; one-sided exact McNemar
P(X>=b | Binomial(b+c,1/2))={g['one_sided_exact_mcnemar_p']}.
AllfourcriteriaPASS: no more wrongvalues, p>=.05, rate<=18, dirty0.
Paired executedT difference{g['candidate_minus_parent_mean_executed_toffoli']},
SE{g['paired_standard_error']} is diagnostic. Outcome final: no relabel, extension,
resampling or different nonce to reverse a failed verdict. No earlier census
is reused. The final tail is independently checked as96 literal nonce-zero X
operations before declaring this sole census.

## Qualified ascending nonce and complete unchanged benchmark

Only after that exact frozen source passed its own gate, the full-state exact
engine/library/binary hashes are checked and the engine is requalified. Eight
additional partial noncecontrols1..8 repeatinproduction, with24protected full
qubit/classical/phase/RNG/curve batches at0,70,140. No approximate arithmetic
filter rejects packets. Production screens ascending1..{sr['highest_screened']},
{len(rows)} actual screens; lowest passingnonce{k}, passes{passes}, all completed
window overrun above{k} through{sr['highest_screened']} retained. Never select byT.
The selectednonce independently passes all9,024 attempts under the protected
replay. Final source changes ONLY depth12_context_cache::IDENTITY_NONCE0->{k}.
Every pre-tail byte equals the gated stream and all96 tail operands are checked.

The unchanged benchmark.sh rebuilds and passes all9,024 shots with0 classical,
0phase-garbage and0ancilla-garbage errors. Harness/scorer/simulator/curve/Cargo/
toolchain/history stay byte-identical; results.tsv is restored after separate
benchmark evidence is saved. Only src/point_add changes are committed. Final
revision{revision}; sourcearchiveSHA256{review['source_archive_sha256']};
patchSHA256{review['source_patch_sha256']}.
SelectedstreamSHA256{b['native_receipt']['stream_sha256']}; canonicalrecordsSHA256
{b['native_receipt']['records_sha256']}; pretailSHA256{b['native_receipt']['pre_tail_sha256']}.

Every source/proof/native/failure/development/gate/nonce/benchmark member is
archived and independently hash-verified locally before upload. Public records
are refreshed immediately before submission. Finite success is not universal
correctness. AttributionGPT-6 sol/Codex; original source/dependency credits
retained. Separate globalproduct research remains active.
"""
assert len(note)>6000;(r/'SUBMISSION-NOTE.md').write_text(note)
deps=json.loads((ws/'breakthrough-groups-context-final-20261020/DEPENDENCIES.json').read_text());deps[0]['rationale']='Inherited precache strong grouped-square arithmetic lineage, now exactdepth12/newcache proofs; not an unchanged entire-parent claim.';deps.insert(0,{'submissionId':'71d9dc7e-550b-480d-8d9e-c2af1989c0d7','rationale':'Exact currentT comparison parent and prior contextcache methodology; new depth12/raw/generic/cache bindings and rows independently regenerated.','evidence':'28a4e93e8cc020282b36413b27edce3cf0ff3ce8'});save('DEPENDENCIES.json',deps)
files={};streams={}
for prefix,directory in[('',r),('gate',gate),('search',search),('finished',research),('proof',proof),('development',development),('grid',grid),('grid-development',griddev)]:
 for p in directory.iterdir():
  if p.is_file()and'resource-preflight'not in p.name and p.name not in['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log','review.log']:
   name=(prefix+'/'if prefix else'')+p.name
   if p.name.endswith('ops.bin'):streams[name]=sha(p)
   else:files[name]=p
pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());assert all(sha(proof/'tool'/p)==h for p,h in pf['tool_source_files'].items())
for p in pf['tool_source_files']:files['proof-tool/'+p]=proof/'tool'/p
for n in['PUBLIC-SOURCE-VERIFICATION.json','SOURCE-FREEZE.json','SUBMISSION-NOTE.md','BENCHMARK-RESULT.json','PACKAGE-RESULT.json']:files['parent/'+n]=ws/'breakthrough-groups-context-final-20261020'/n
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':streams,'scope':'Complete205-source, exactdepth12/raw/generic/cache bindings/native34/proof9/runtime2, fixed architecture development, fresh finalsource development/sole declared gate, all qualifiednonce screens andunchanged9024benchmark. Originalfailedsetup fixtures linked separately; no credentials/process listings.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as archive:
 for n,p in sorted(files.items()):archive.add(p,arcname=n,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
