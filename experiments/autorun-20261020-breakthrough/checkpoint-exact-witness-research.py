import gzip,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=root/'experiments'
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip();assessment=ex/'breakthrough-assessment-20261020';snap=assessment/json.loads((assessment/'LATEST.json').read_bytes())['snapshot'];records=json.loads((snap/'PUBLIC-RECORDS.json').read_bytes());assert records['leaders']['product']['id']=='1829986e-675c-4fbf-bb28-22f2f95246c4';raw=(snap/'public-submissions.json').read_bytes();json.loads(raw);(snap/'public-submissions.json.gz').write_bytes(gzip.compress(raw,mtime=0));names=['leader-product.json','leader-qubits.json','leader-toffoli.json','PUBLIC-RECORDS.json','public-submissions.json.gz'];sha=lambda b:hashlib.sha256(b).hexdigest();(snap/'SNAPSHOT-MANIFEST.json').write_text(json.dumps({'raw_api_sha256':sha(raw),'files':{n:sha((snap/n).read_bytes())for n in names},'scope':'Fresh official public record snapshot; T2bd remains minimum, newproduct1829 supersedes acd0.'},indent=2)+'\n');(snap/'.gitattributes').write_text('* -text\n')
fronts=['breakthrough-value-ir-audit-v2-20261020','breakthrough-value-ir-audit-v3-20261020','breakthrough-value-ir-audit-v4-20261020','breakthrough-value-abstract-audit-20261020','breakthrough-dense-exact-verifier-20261020','breakthrough-public1829-reproduction-20261020','breakthrough-exact-witness-ripple-20261020'];verified={n:json.loads((ex/n/'LOCAL-VERIFICATION.json').read_bytes())['members']for n in fronts};assert sum(verified.values())==196;failed='breakthrough-exact-witness-ripple-v2-20261020';assert json.loads((ex/failed/'LOCAL-VERIFICATION.json').read_bytes())['members']==23
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),latest_public_snapshot=snap.relative_to(root).as_posix(),public_product={**records['leaders']['product'],'Q':1234,'T':755314,'product':932057476,'source':'3eefcf216ca37cba0ae3f56212d6b1302844a249'},product_candidate_status='SUPERSEDED_BY_NEW_PUBLIC_RECORD; oldPASS finalagainstacd0 retained, no currentrecord claim',active_jobs=[{'directory':'breakthrough-exact-witness-ripple-v3-20261020','pid':3111201,'purpose':'Native4witness/sum1/group1 andall5fullsquarecaller controlsPASS; fixedfullconstructor/resourcegrid generating. No score/gate/nonce.'},{'directory':'breakthrough-exact-witness-development-20261020','pid':3116282,'purpose':'Waitforcompletegrid, fresh512x64/source label exact-witness-resource-development-20261020-v1 againstexactT2bd; actual-resource-only selection, allfailure evidence retained.'},{'directory':'breakthrough-public-best-drop-nonce-v2-20261020','pid':3045633,'engine_pid':3046104,'purpose':'Finish original finite1..65536 only, over62000screens/noPASS atcheckpoint. Infinitecontinuation/upload pipeline intentionally stopped idle; source/gate retained asobsolete research.'}],active_submission=None,cycle11_verified_completed_evidence=verified,cycle12_verified_completed_evidence={failed:23},public1829_reproduction=json.loads((ex/'breakthrough-public1829-reproduction-20261020/RESULT.json').read_bytes()),next_product_front='New publicproduct1829/source3eef/Q1234/T755314 exactreproduction complete. PriorQ1233/acd0 gatedsource isobsolete andmustnotupload. Currentmainfront exactfull259 witnessconsolidation/sharedsum onstrongTparent; selectactualresources, freshcacheproof/wholebindings/literal0/sourcefreeze, freshdevelopment andownfinalgate vs exactcurrentT2bd, qualifiednonce/unchanged9024benchmark/localreview/autosubmit. Then pursue productusingnewpublicsource, never reuseoldgateverdict.',new_official_summary='Our2bd Q1464/T747218 remains officiallyverified independentT minimum. Newglobalproduct1829 Q1234/T755314/932057476. Globalproduct goalACTIVE, no completion.')
state['superseded_followons']=json.loads((ex/'breakthrough-public-best-drop-final-20261020/SUPERSEDED.json').read_bytes());state['superseded_followons']['local_watch']='PID40820 exited1 as expected from intentionalreviewstop; zero benchmark/upload attempts, not a candidatebenchmark failure.';state['dense_exact_verifier']=json.loads((ex/'breakthrough-dense-exact-verifier-20261020/RESULT.json').read_bytes());state['value_abstract_negative']='Native14 and24fullstream protected value comparisonsPASS, but zero certifiedknown output bits onall8fixtures. No useful rejectionfilter, no nonce rejected; no quantum resource result. V4classicalaliases reduce dependencies but still5792product/410T measurementdefs at128rounds.';(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
readme='''## Public references refreshed · 21 October 2026, 04:03 SGT

The latest public product record is **1,234 × 755,314 = 932,057,476**,
[submission 1829986e](https://api.ecdsa.fail/api/submissions/1829986e-675c-4fbf-bb28-22f2f95246c4).
Its unchanged 9,024-shot benchmark, source files and published stream reproduce
locally. Our [747,218-Toffoli result](https://api.ecdsa.fail/api/submissions/2bd0f979-ab55-4f91-8133-68a08febaa67)
remains the independent Toffoli minimum in the fresh public snapshot.

[Public-record reproduction and provenance](experiments/breakthrough-public1829-reproduction-20261020/RESULT.json)

'''
addition='''## 21 October 2026, 04:15 SGT: new public baseline; exact full-width arithmetic

Fresh19:54UTC1714records: accepted1829986e/source3eefcf21 becomesproductminimum
Q1234/T755314/product932057476. Our2bd Q1464/T747218 remainsTminimum; width670/e2.
Newpublicsource reproduced WITHOUT edits:186source/17protected matchGit objects,
unchanged9024benchmarkPASS,total6815950442, exactpublishedstream16567ee1,
SFf5757099/sourcearchive0a420e46. Every22evidence members verifiedlocally.

OurQ1233/bestdrop gatePASS againstoldpublicacd0 remainsfinal; not re-judged or
rerun. Newpublicrecord removesits expectedproductmargin. StoppedONLY verified
idlecontinuation3074390 andidlefinalwatch3078510/child3078511 BEFORE any new
screens/benchmark/upload. SUPERSEDED.json preservesofficialnewrecord/commands/
zeroattempts. Localwatch40820 exit1 is expectedintentionalstop, not a benchmark
failure. Initialqualified finite1..65536 search3045633/3046104 mayfinishunchanged;
over62000completed/noPASS atcheckpoint. Noinfinitecontinuation orobsoleteupload.
Preparedscripts remainresearchhistory; neverresumeoldsource againstnewrecord.

Exact arithmetic opportunity onstrongTparent: allfive oldwitness translations
runFULL259bits becauseSQC_G259. Their sum is -w*(2^32+977) mod2^259, w0..7.
Public1829's13-lowbit polynomial is adapted to a singleFULL259bit ripple,
REQUIRINGg>=n; its public59bitcut isNOT imported. No new group/reduction/witness
cutoff; strong28bitwrap witness, fullgroup tails, windows/rounds/exactsplits stay.
Separate exact sharedsum copies128bits whilebothoperands live andusesoldexact
freeerase; extraQ allowed forindependentT. Fixed5cases beforeinputs: exactf8c833
precache control, rippleatoldcaps, ripplewide, sharedsumwide, bothwide; widecaps
global1664/square1536. Sourceonlypoint_add,17protected unchanged.

V1setup stoppedbeforefreeze/native tests becausea textualsumneedleoccurselsewhere;
partialsource/logs preserved18members. V2scopes ONLYsub_square_g1m, thennative
newcomponent fails after deliberatefault. Diagnosis: inheritedheo::passthrough
caches firstread processswitch inOnceLock<HashMap>; fault1 stayedactive after
set_var0. Oldreferencepassed. OriginalfrozenV2/nativefailures preserved23members.
V3readsALL3newresearchswitches directly throughstd::env andadds fault-then-clean
regression. All4witness testsPASS: polynomialw0..7/modulartranslation widths35,
59,64,129,259; full259old/new phase/guard/dirty checks; faultdetection; faulttoggle.
Sharedsum small/widebasis/control/phase/cleanup testPASS. Groupplan1 andall5
existingfullsquarecaller unitsPASS (their6historical walk-domain exclusions
unchanged/disclosed). No statistical gate/census/nonce verdict existsfornewgrid.
Fullconstructor generation nowrunning; mustreproducecontrolf8c833 before any
resource interpretation. Staticweights are diagnostics, never scoredToffolis.

Queued development3116282 waitsforcompletegrid. Onefreshlabel
exact-witness-resource-development-20261020-v1,512x64/source,4workers/8protected
scalarbatches each vs exactpublishedT2bd stream63370be6. Selectminimum actualmeanT,
tieQthenmode, solely byresources amongpredeclarednative-correct architectures;
preserveallwrong/phase/dirty/otherdifferences. Nofailure-based hiddenselection.
Thenfreshcacheproof/fullraw/generic/cachebindings, literal0/sourcefreeze/native,
freshfinisheddevelopment, OWN sole finalgate vs exactthen-currentT2bd, qualified
ascendingnonce/protected9024/unchangedbenchmark/localmemberverification before
automatic GPT-6sol/Codex submission. Globalproduct goalremainsACTIVE.

Verifierresearch remainsseparate: IRv2native8 reachesfixedpoint321rounds,
product7510/T2187live RNGdefs; v3native10/128rounds7393/2087; v4native12/128rounds
5792/410. Countsareinternal dependency nodes, NOT quantum resources. Threevalued
auditnative14/24fullsource protected finalvalue comparisonsPASS, butall8fixtures
haveZEROcertifiedknown outputbits; no usefulRNG-free rejectionfilter. Neverused
to rejectanynonce orclaimquantumimprovement. Allnegative evidence retained.

Exact dense-survivor verifier passes8partialnonce/24protectedfullstate controls,
all1024productnonce terminalkinds/firstwitnesses/counts matchoriginalengine, plus
knownpassingofficialTdepth12nonce41/all141batches/protected9024. Additional2057
controlattempts recorded, repeatproduction1024, notnewselection. Fullcontroltime
29.96475s vs37.94737s (~1.2664x), no scoreclaim. Sourcefreeze011bf97c/binaryebe4abc2.
Productionengine/source unchanged. Anyfuture newsource needsfreshqualification.

Cycle11sevenfronts196 andcycle12onefront23members allhashverifiedlocally. Original
source/protected files, patches/logs/streamhashes andfailures retained; inventories
stayserver-only. Allpreexistinguserroot/submodule edits preserved. Lastlocal
checkpoint9006f17; default-branchpush remainsblockedbyautomaticapprovalreview,
pendingexplicituserapproval. Do notbypass. Localwork/authorizedchallengeuploads
continue; unrelatedserverQOBjobs/chemistry untouched.

'''
for path,prefix in[('README.md',readme),('docs/research-plan.md',addition),('docs/AGENT_HANDOFF.md',addition)]:
 p=root/path;data=prefix.encode();assert not p.read_bytes().startswith(data);p.write_bytes(data+p.read_bytes());blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+path)).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
dirs=fronts+[failed,'breakthrough-exact-witness-ripple-v3-20261020','breakthrough-exact-witness-development-20261020','breakthrough-public-best-drop-nonce-continuation-20261020','breakthrough-public-best-drop-final-20261020']
scripts=['CURRENT-ACTIVE.json','checkpoint-exact-witness-research.py','prepare-product-search-continuation.py','prepare-product-best-final.py','prepare-product-best-seal.py','product-best-sealer-tail.py','prepare-product-local-watch.py','watch-product-best-local.py','collect-product-best-final.py','test-product-search-accounting.py','prepare-value-ir-v3.py','prepare-value-ir-v4.py','prepare-value-abstract-audit.py','prepare-dense-exact-verifier.py','read-product-progress.py','supersede-public-best-drop.py','prepare-public1829-reproduction.py','prepare-exact-witness-grid.py','prepare-exact-witness-grid-v2.py','prepare-exact-witness-grid-v3.py','prepare-exact-witness-development.py','prepare-cycle11-collection.py','seal-research-cycle11.py','collect-research-cycle11.py','prepare-cycle12-collection.py','seal-research-cycle12.py','collect-research-cycle12.py']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+[snap.relative_to(root).as_posix()];subprocess.run(['git','-C',str(root),'add','--',*paths,':!**/public-submissions.json'],check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();allowed=paths+['README.md','docs/research-plan.md','docs/AGENT_HANDOFF.md'];assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged);assert not any('resource-preflight'in p or'/candidate/'in p or'/observer/'in p or'/tool/'in p or p.endswith('ops.bin')for p in staged);subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve fresh public product baseline and exact arithmetic controls; retire obsolete follow-ons'],check=True);print(git('rev-parse','HEAD').decode().strip())
