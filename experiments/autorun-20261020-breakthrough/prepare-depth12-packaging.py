from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-groups-context-final-20261020';r=a.parent/'breakthrough-depth12-final-20261020'
s=(old/'seal.py').read_text();end=s.index("proof=ws/'breakthrough-groups-safe-context16-20261020'");s=s[:end]
for before,after in {'breakthrough-groups-context-finished-20261020':'breakthrough-depth12-finished-20261020','breakthrough-groups-context-final-gate-20261020':'breakthrough-depth12-final-gate-20261020','breakthrough-groups-context-nonce-20261020':'breakthrough-depth12-nonce-20261020','groups-context230-final-20261020-v1':'depth12-context-final-20261020-v1','Cache230 independently exact contextual products on officialT747453 at nonce':'Exactdepth12 square andfreshly proved230 contextcaches at nonce','Complete unchanged benchmark of230 independently exact contextual product leases on officialT747453; actualQ1464 unchanged. Fresh publicminimum checked before upload; no globalproduct claim.':'Complete unchanged benchmark of exactdepth12 plus freshly proved230existing-wire caches on strong grouped arithmetic; Q1464. Targets independentT versus current71, no globalproduct claim.'}.items():s=s.replace(before,after)
needle="assert b['status']=='COMPLETE_UNCHANGED_BENCHMARK_PASS'";assert s.count(needle)==1;s=s.replace(needle,"assert b['rounded_mean_executed_toffoli']<747226,'Lowest passing packet does not improve currentT; never choose anothernonce by cost'\n"+needle)
s+='''
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
'''
ast.parse(s);(r/'seal.py').write_text(s);shutil.copyfile(old/'review.py',r/'review.py')
s=(old/'submit.py').read_text().replace('8d0fef2b-a7f6-40a7-9b3c-f800073cf2c5','71d9dc7e-550b-480d-8d9e-c2af1989c0d7');ast.parse(s);(r/'submit.py').write_text(s)
print(r)
