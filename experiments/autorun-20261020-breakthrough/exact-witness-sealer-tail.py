proof=ws/'breakthrough-exact-witness-context-20261020';development=ws/'breakthrough-exact-witness-finished-development-20261020';grid=ws/'breakthrough-exact-witness-ripple-v3-20261020';griddev=ws/'breakthrough-exact-witness-development-20261020';component=json.loads((proof/'RESULT.json').read_text());pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['witness'];ar=json.loads((research/'RESULT.json').read_text());ps,cs=g['summaries']['parent'],g['summaries']['candidate'];selection=json.loads((griddev/'RESOURCE-SELECTION.json').read_text());gr=json.loads((grid/'RESULT.json').read_text());rf=json.loads((research/'SOURCE-FREEZE.json').read_text())
assert component['native_controls']==9 and component['output_qubits']==b['qubits']and ar['native_tests']==7 and ar['independent_proof_controls']==9;assert not pc['different_target_lanes']and not pc['different_other_lanes'];assert gr['native_components']==5 and gr['group_plan_controls']==1 and all(x['exit']==0 for x in gr['fullsquare_units']);assert selection['selected']['mode']==rf['fixed_resource_mode'];assert len(f['source_files'])==205
note=f"""Model: GPT-6 sol
Harness: Codex

# Exact full-width witness consolidation and shared-sum cleanup, with fresh cache proofs

The unchanged original challenge benchmark rebuilds the final frozen source and
passes all9,024 shots: peak logicalQ{b['qubits']}, rounded mean executedToffolis
{b['rounded_mean_executed_toffoli']}, exact sum{b['total_executed_toffoli']}, exact
mean{b['mean_executed_toffoli']}, product{b['product']}. Compared with official
2bd0f979/Q1464/T747218 this saves{747218-b['rounded_mean_executed_toffoli']}roundedT.
These are complete locally passing benchmark measurements pending official
evaluation, targeting the independentToffoli objective. The publicglobalproduct
record islower; no globalproduct/width record isclaimed. Finitepassing evidence
is not a universal full-curve correctness proof.

## Exact arithmetic change and source lineage

The statistical parent is exactpublishedsubmission2bd0f979-ab55-4f91-8133-
68a08febaa67, source36e37af06d56bade9bfaedc0a252a81bbe3858b8, fullselectedstream
63370be6078a4a80454d5174a5f07bfac094fea6af3dd526f77dc8194012cc29. All205point-add
and17protected Git-object bytes were checked against its complete benchmark.
We compare that exactstream, not a proxy oroldreport. Our constructor starts
from the independentlyfrozen strongdepth12 precache prototypef8c83372. Its
unchanged fullcontrol reproduces byte-for-byte before newresource measurements.
We do not claim that the entire public2bd constructor is unchanged.

The old C-direct square applies five FULL259-bit translations: subtractw,
subtract16w, add64w, subtract1024w andsubtract2^32w, wherew isthreebits. Their
combined translation is -w*(2^32+977) modulo2^259. Submission1829986e/source
3eefcf216ca37cba0ae3f56212d6b1302844a249 supplies the exact13lowbit Boolean
polynomial for977*w andthe sharedsum construction. We adapt its polynomial
to ONE FULL259-bit subtraction. Its original59-bit cutoff is deliberately
extended to the full register; an explicit g>=n requirement verifies that
every originaltail was fullwidth. Polynomialtruth is checked for allw0..7.
This is an exact consolidation, not a new arithmetic precision orcarry cutoff.
We do not import that publicentry's newgroup/reduction/witness cutoffs.

Separately, form the square's C sum in a fresh128-wire copy while bothoperand
halves remainlive. After the C rows, erase the sum with the inherited exact
measurement/CZ sum-erase using both liveparents. This avoids the old in-place
sum restoration. All copies/helpers/measurementrepairs remain in the emitted
circuit and are counted. The private allocation budget permits the copy;
protected actualQ is measured, not inferred from the budget.

Strong28-bit wrapwitness, full259-bit correction, fullgrouped carrytails, exact
square splits, public140 schedule/uniform+2 comparisons, plainpool and native
rail/G6 components remain. No window, witness precision, cut orround is lowered.
Inherited approximations elsewhere remain. Original source notices/credits
and data are retained. Polynomial andsharedsum credit1829986e/JackyLee0424;
grouped-square/leaf andsum-erase lineage acd0d88e/e3b5c51f; rail/G6 andour earlier
contextproof methods retain their dependency credits. No novelty oruniversal
correctness claim ismade for inherited primitives.

## Fixed resource grid and native controls

Before anyfresh full-point development the fixed architecture grid contains:
strongdepth12control, fullwidthripple at oldcaps, ripple at widercaps, sharedsum
at widercaps, andboth at widercaps. Widecaps areglobal1664/square1536; larger
workspace is permitted for the independentToffoli objective. Allfive complete
streams have protectedQ1464. The old andwide ripple streams are identical.

Four directwitness tests pass: exact U512 modulartranslation for w0..7 at
registerwidths35/59/64/129/259; full259 old/new value/phase/dirty/capturedguard
checks; deliberatewrongproduct detection; and fault-then-clean isolation in
oneprocess. The separate sharedsumtest covers small/wide operands through128bits,
copiedsum value, liveoperand restoration, phase andallhelper cleanup. Groupplan
structurecontrol and allfive complete native squarecaller units pass. Their
six historical walk-domain edge exclusions are unchanged and disclosed in raw
logs; these finite tests do not certify arbitraryfield behavior universally.

Two earlier setup/native attempts are preserved. V1 stopped before sourcefreeze
or native tests because a textualneedle also occurred in another squarepath;
the correction scopes onlysub_square_g1m. V2's first deliberatefault test cached
fault1 through inherited heo::passthrough's OnceLock map, so later set_var0 did
not disarm it. The oldreference passed butnewtests remainedfaulted. V3 reads
allthree newresearch switches directly via std::env andadds the same-process
fault-then-clean regression. Arithmetic, full259range andfixedcases areunchanged.
Original partial/frozen sources, nativefailures andlogs remainavailable; no
statistical gate wasrun orrepeated in thoseattempts. In finalproduction the
witnessfault is cfg(test) only, absent from the submitted executable; the old
research groupfault branch andrawdump path are inactive/removed fromthe caller.

One fresharchitecture-development label
exact-witness-resource-development-20261020-v1 runs512x64/source,4workers and
8protectedscalarbatches each, comparing allfixedstreams against exactT2bd.
Everytarget/other register andwrong-value identity matches, dirty0. Selection
is minimum actualmeanT, thenQ, thenmode, under a policy declared beforeinputs;
no circuit/table/cut is tuned to failureidentities orchallengepackets.
Selectedmode{rf['fixed_resource_mode']}, selectionSHA256{sha(griddev/'RESOURCE-SELECTION.json')}.
All gridmeans/staticweights are diagnostics, not scoredresults. This selection
precedes cacheproof, finalsource, solefinalgate andnonce inputs.

## New exact existing-wire proofs and whole-stream bindings

The same16384-operation, samecapturedlexicalguard proof searches earlierproduct
endpoints. Fingerprints only nominate; exact BooleanXOR/AND expressions on
arbitrarycut values andclassical/measurement values must prove endpoint product
equality. Donors must be resetclean orprovedexactlyzero; no-touch, scope and
non-overlap constraints apply. Unknownexpressions are rejected. Nine independent
native value/phase/guardcapture/mutation/RNG/alias/donor/fault controls pass
before the newscan. Nominees{component['proposed']}, provenleases{component['leases']},
rejections{component['proposed']-component['leases']}, maxdonor{component['max_donor']},
zeroaddedcachewires, protectedoutputQ{component['output_qubits']}.

A product iscomputed once in an existingzero donor, copied at two targetsites,
then X-measured/reset with its exact guarded CZphase repair. Every operation is
inside the circuit. No old230-row table orindex is transported to changedsource.
The finalsource fixes the selectedmode as a literal; binds EVERY rawoperation,
runs the unchanged genericpipeline ONCE, binds EVERY genericprefix, reconstructs
the checked inherited96-op identitytail, binds the entire proofinput, verifies/
removes that tail, applies the literal newproofrewriter/rows, binds EVERY output
prefix, then appends literalnewnonce0. No externalloader oruncounted quantumwork.
Actual inheritednonce{rf['parent_historical_nonce_removed']} isdecoded andchecked;
no assumption that an environmentvariable overrides a pinned recipe ismade.
Sourcefreeze has205point-add and17protected files. Runtimecachephase/guard/fault,
witness4, sharedsum1 andgroupplan1 tests total7 pass after finalfreeze; independent
proof9 andallfixedcaller controls are retained withhash provenance.

## Fresh finished-source development and sole final gate

Finisheddevelopment label{pd['label']},512x64/source,4workers/8protectedscalar
batches each: parent/candidate wrongvalues{pd['summaries']['public2bd']['value_shots']}/
{pd['summaries']['witness']['value_shots']}; target/other differences0, no newwrong
ornewpassing identities, dirty0. The finalsource is notaltered after theseinputs.

Solelabel{g['label']}, declared{d['declared_at_utc']} BEFORE census onnonce0.
32768batchesx64=2097152shots/source,8workers and8protectedscalarbatches each.
Exactparent2bd stream above; candidateSF{g['candidate_source_freeze_sha256']}.
DeclarationSHA256{sha(gate/'GATE-DECLARATION.json')}; result{sha(gate/'GATE-RESULT.json')}.
Parent/candidate wrong-value shots{ps['value_shots']}/{cs['value_shots']}, newwrong
{g['new_value_failing_shots']}, newpassing{g['new_value_passing_shots']}, sameidentities
{g['value_failing_shot_identities_equal']}; phaseshots{ps['phase_shots']}/{cs['phase_shots']},
dirty{ps['dirty_shots']}/{cs['dirty_shots']}; failedbatches{ps['failed_batches']}/{cs['failed_batches']}.
Candidatefailedbatches per9024packet{cs['failed_batches_per_9024_packet']}.
Discordant newlyfailing b={g['newly_failing_batches_b']}, newlypassing
c={g['newly_passing_batches_c']}; exact one-sided McNemar
P(X>=b | Binomial(b+c,1/2))={g['one_sided_exact_mcnemar_p']}.
AllfourcriteriaPASS: valuefailures<=parent, p>=.05, failurepacket<=18, dirty0.
PairedTdifference{g['candidate_minus_parent_mean_executed_toffoli']} andSE
{g['paired_standard_error']} are diagnostic, not scores. OutcomeFINAL: no rerun,
relabel, morebatches, resampling oranothernonce toreverse a failedgate. No old
verdict is reused. All96literalzero-tail records are independentlydecoded before
declaring this census. Full label/input/count/statistics are archived.

## Qualified ascending nonce and complete unchanged benchmark

Only after this finishedsource's ownPASS, frozen exactengine/source/library/
binary hashes arechecked and the engine requalified on this exactstream. Eight
additionalpartialnoncecontrols1..8 repeatproduction;24protected fullqubit/bit/
phase/RNG/curve batches at0,70,140. No arithmeticmodel orvalueIR rejectsanynonce.
Production ascending1..{sr['highest_screened']}, {len(rows)} actualscreens; lowest
completePASS{k}, allpasses{passes}, completedwindow overrun above{k} through
{sr['highest_screened']} retained. Neverchoose byToffoli cost. Selectednonce also
passes theprotected complete9024-attempt replay. Finalsource changesONLY
witness_context_cache::IDENTITY_NONCE0->{k}. Everypre-tail byte equals thegated
stream andall96tail operands arechecked. No circuit/table/cut is tuned toapacket.

Unchangedbenchmark.sh rebuilds andpasses9024shots:0classical,0phase-garbage,
0dirtyancilla. Harness/scorer/simulator/curve/Cargo/toolchain andhistoricalresults
remainbyte-identical; appendedbenchmark evidence saved andresults.tsvrestored.
Onlysrc/point_add changes arecommitted. Revision{revision}; sourcearchive
{review['source_archive_sha256']}; patch{review['source_patch_sha256']}; selectedstream
{b['native_receipt']['stream_sha256']}; canonicalrecords{b['native_receipt']['records_sha256']};
pretail{b['native_receipt']['pre_tail_sha256']}.

Allcurrent candidate/proof/native/development/gate/nonce/benchmark evidence and
source members are independentlyhash-verified locally before upload; failed
earlierresearch ispreserved separately andlinked by immutablehashes. PublicT
records arerefreshed immediately before submission. AttributionGPT-6 sol/Codex;
alloriginaldependency/source credits retained. Globalproduct research continues.
"""
assert len(note)>6000;(r/'SUBMISSION-NOTE.md').write_text(note)
deps=json.loads((ws/'breakthrough-depth12-final-20261020/DEPENDENCIES.json').read_text());deps.insert(0,{'submissionId':'1829986e-675c-4fbf-bb28-22f2f95246c4','rationale':'Exact three-bit lowproduct polynomial and sharedsum construction, adapted toFULL259 with no new publiccutoffs imported. Original notices/credits retained.','evidence':'3eefcf216ca37cba0ae3f56212d6b1302844a249'});deps.insert(0,{'submissionId':'2bd0f979-ab55-4f91-8133-68a08febaa67','rationale':'Exact currentToffoli statistical comparison parent and strongdepth12/contextproof lineage. New exact arithmetic andfreshcache rows/bindings; not an unchanged-entire-constructor claim.','evidence':'36e37af06d56bade9bfaedc0a252a81bbe3858b8'});save('DEPENDENCIES.json',deps)
files={};streams={}
for prefix,directory in[('',r),('gate',gate),('search',search),('finished',research),('proof',proof),('development',development),('grid',grid),('grid-development',griddev)]:
 for path in directory.iterdir():
  if path.is_file()and'resource-preflight'not in path.name and path.name not in['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log','review.log']:
   name=(prefix+'/'if prefix else'')+path.name
   if path.name.endswith('ops.bin'):streams[name]=sha(path)
   else:files[name]=path
pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());assert all(sha(proof/'tool'/path)==h for path,h in pf['tool_source_files'].items())
for path in pf['tool_source_files']:files['proof-tool/'+path]=proof/'tool'/path
for name in['PUBLIC-SOURCE-VERIFICATION.json','SOURCE-FREEZE.json','SUBMISSION-NOTE.md','BENCHMARK-RESULT.json','PACKAGE-RESULT.json']:files['parent/'+name]=ws/'breakthrough-depth12-final-20261020'/name
failed={}
for prefix,name in[('setup-v1','breakthrough-exact-witness-ripple-20261020'),('native-v2','breakthrough-exact-witness-ripple-v2-20261020')]:
 directory=ws/name;package=json.loads((directory/'PACKAGE-RESULT.json').read_text());failed[prefix]={'directory':name,'archive_sha256':package['archive_sha256'],'manifest_sha256':package['manifest_sha256'],'members':package['members']}
 for path in directory.iterdir():
  if path.is_file()and'resource-preflight'not in path.name and path.suffix not in['.gz','.bin']and path.name not in['EVIDENCE-MANIFEST.json']:
   files[prefix+'/'+path.name]=path
save('EVIDENCE-MANIFEST.json',{'files':{name:sha(path)for name,path in files.items()},'streams_retained_on_server':streams,'separately_preserved_failed_experiments':failed,'scope':'Complete205source/17protected exactfull259 witness/sharedsum andfreshcache proofs, native5/group1/full5caller/proof9/runtime7, fixedresource development, finalsource freshdevelopment/solegate/qualifiedallnonce/unchanged9024benchmark. Everyfinalmember locallyverified; originalfailedsource archives separatelypreserved andhashlinked. No credentials/process inventories.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as archive:
 for name,path in sorted(files.items()):archive.add(path,arcname=name,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
