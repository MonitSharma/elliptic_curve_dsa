import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent
def git(*args,data=None):return subprocess.check_output(['git',*args],cwd=root,input=data,stderr=subprocess.PIPE)
assert not git('diff','--cached','--name-only').strip();now=datetime.now(timezone.utc).isoformat();state=json.loads((a/'CURRENT-ACTIVE.json').read_text());state['at_utc']=now;state['latest_public_snapshot']='experiments/breakthrough-assessment-20261020/snapshots/20261020T184845Z'
state['active_jobs']=[{'directory':n,'pid':p,'purpose':purpose}for n,p,purpose in[
 ('breakthrough-public-best-drop-context-20261020',3032091,'Select cheapest complete Q1233 exact profile from both finished fixed grids, solely by static resources before fresh point inputs; regenerate nine-control zero-wire cache proof.'),
 ('breakthrough-public-best-drop-finished-20261020',3032288,'Freeze selected literal mode, all177source/17protected, full input/newoutput bindings and checked inherited-tail removal/newliteral0; native runtime1/fullgeneration.'),
 ('breakthrough-public-best-drop-development-20261020',3033418,'After finalsource, fresh512x64/source labelpublic-best-drop-development-20261020-v1, full outputs/phase/dirty/T and8protectedscalarbatches each; no score.'),
 ('breakthrough-public-best-drop-final-gate-20261020',3036591,'After finished source/development, independently decode96 literal zero-nonce ops, verify current exactpublicacd0 and adequate resource margin, then sole predeclared131072x64/source finalgate; no declaration yet at checkpoint. Never rerun/relabel/extend a verdict.'),
 ('breakthrough-grouped-exact-resource-grid-v2-20261020',3022917,'Native34/fullsquarecaller/fault controls pass; fixed full a871/dc1478 controls exact, d12/d16/square1536/walk1664 constructions. Read completion marker and actual diagnostics.'),
 ('breakthrough-grouped-resource-development-20261020',3034160,'After fixed source/resource grid, one fresh512x64/source full-output and actual-T comparison vs official71. Proxy unreliable for OR-of-measurement guards. No finalgate/nonce/score.')]]
state['next_product_front']='Best fixed exact reverse profile is r012 [0,1,2], sameQ1233/proxy755906, sourceframe0429accf; originalwidthproxy755936.75. All lower profiles failed existing guards. Regenerate cache, freeze wholeboundsource/literalnonce0, fresh actualresource development, then the queued sole finalgate only if resource/currentparent checks pass. Qualifiedascendingnonce/fullunchanged9024benchmark/localreview must follow PASS before autoupload.'
state['nonce_disclosure_correction']='Read PROTOTYPE-TAIL-CORRECTION.md. Public required_env/env_raw ignored process TAIL_NONCE0, so prototype streams retained inherited1052246623534. No nonce screening or officialbenchmark ran on them. Finished rmin/newbest wrappers parse/check/remove actualoldtail and appendliteral0; rminSF recordsold1052246623534/new0. Finalgate independently verifies all96zero-tail ops. Do not rewrite sealed evidence or call oldprototypes nonce0.'
state['rmin_intermediate']={'status':'COMPLETE_BOUND_NONCE0_RESEARCH_SOURCE_UNGATED_SUPERSEDED_BY_BETTER_STATIC_PROFILES','Q':1233,'diagnostic_weight':755806,'leases':113,'source_freeze_sha256':'6f90ab4c26837e5a23dd9e6403bdee184f142396a4dafd0f3b32cc23b9ac852b','stream_sha256':'6544742918ecca596d36a7554d82e33ce6f5b65842650c417cefd62fa20cebbf','old_nonce_checked_removed':1052246623534,'new_identity_nonce':0,'scope':'No finalgate/nonce/benchmark or score. Best fixed resource profile is selected before new point inputs.'}
state['new_negative_findings']={'expanded_caps':'CompleteQ1235..1248/staticcost tradeoffs noncompetitive for product; do not call their proxy counts scores.','context_65536':'Native9, exactlysame113leases/output as16384.','guard_restricted_live':'Native9; widthcache5hits/public3hits/latestT0hits, exactlysame outputs as original6-control engine on common inputs. No new gain.','width1232':'Prefix/reverse exactport native14/fullpublic/1233controls pass. CompleteQ1232/proxy756640.625, stronger+1/+2 caps complete but costly. Cache native9 only31leases, noncompetitive. Cap1231fails existingguards.','value_cone':'V1compile-only failure u64/u32 SSA IDs retained. V2native4PASS/read-onlyaudits: public22830 andT5260live measurement outcomes, retains almostallToffolis; no justified fast value-only rejection shortcut. No filter/nonce rejection used.','group_fixture_failures':'Originalgroupgrid run1/faultfixture missingcap and resumed1/leafunit missingcap bothpreserved. Correctedfault reached122wrongoutputs/43phasebad in128shots. V2adds cap onlycfg(test), all34controls/fullunits/fault pass, unchanged production arithmetic. No gate verdict rerun.'}
for cycle,names in[(7,['breakthrough-public-acd0-exact-width-v2-20261020','breakthrough-public-width1233-context-20261020','breakthrough-public-prefix27-width-20261020','breakthrough-public-width1233-development-20261020']),(8,['breakthrough-public-width1233-context65536-20261020','breakthrough-public-width-live-20261020','breakthrough-guarded-live-products-20261020','breakthrough-public-prefix27-width-v2-20261020','breakthrough-grouped-exact-resource-grid-20261020','breakthrough-public-width1232-context-20261020'])]:state[f'cycle{cycle}_verified_completed_evidence']={n:json.loads((root/'experiments'/n/'LOCAL-VERIFICATION.json').read_text())['members']for n in names}
state['preservation']='Cycle7 fourfronts203 andcycle8 sixfronts340 archive members fullyverifiedlocally. Cycle9sixcompletedfronts collection inprogress; inspectcollector receipt before claiming allverified. No new official result or gateverdict at checkpoint. Rootlastcommitb123a943; pushesremainblockedpendingexplicitapproval, no bypass. Preserve userroot/submodule edits and unrelatedserverjobs.'
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
prefix='''## 21 October 2026: exact carry-cost pipeline and disclosure correction

Latest18:48UTC snapshot1712records: productacd0 Q1234/T756265/933231010,
width670/e2 andour independentT747226/71 unchanged. Globalproductgoal active;
auto-submit eachcomplete verified current-record improvement asGPT-6sol/Codex.
No new finalgate/nonce/benchmark or scored result at thischeckpoint.

Exactprefix27 port/reverse122drop3 passes14nativecontrols andfullpublic3d7c/
old1233/52a0 controls. CompleteQ1232/proxy756640.625; stronger+1/+2 profiles also
build butcost more, cap1231fails oldguards. Fresh nine-control contextproof finds
only31existingwire leases, so product remainsnoncompetitive. Width1233 oldcache
fresh512x64 has55wrongvalue shots sameIDs asparent,dirty0,27target differences
confinedto jointlywrongvalues; actualmean cost stilltoo high. Larger65536proof
context returns exactlysame113leases. New guarded-parity native9 returns same
5/3/0hits on widthcache/public/currentT as priorengine, no new resource gain.

Exact carry-drop profiles reduce regenerationcost while keeping every arithmetic
window/witness21/round/onefoldrange andallcapacityguards. Fixedrmin1/2/3 builds
Q1233/proxy755919; r1 0/1/3 755911; r2 0/2/3 755917.25; r9 1/2/2 755914. New
fixedextension reproducespriorr1/dd4d exact; profiles0/0/0,0/0/1,0/0/2,0/1/1
fail originalguards,0/1/2 buildsQ1233/proxy755906/frame0429accf. Everygrid source
frozen beforeinputs; native9/passcontrols mandatory. These are diagnostic costs.

Best-drop pipeline chooses minimumstaticcost from both fixed grids before new
pointinputs, regenerates9-control zero-added-wire caches, freezes completebound
177source/17protected andliteralnewnonce0, then fresh512x64 full-output/Tdevelopment.
Queuedsole finalgate plans131072x64/source, onefreshlabel declared before census,
resource/currentpublicparent preflight, independent96-op zero-tail check andall
fourstatisticalcriteria. Outcome final: no rerun/relabel/extension ornonce to
reverse failure. Qualifiedascendingnonce/full9024benchmark/localmemberreview
follow onlyPASS. No finaldeclaration exists yet; inspectactualgate files/status.

Disclosurecorrection: processTAIL_NONCE0 didnot override publicrequired_env/
env_raw recipe. Publicwidth/cap/drop prototypes andpreserving proofoutputs kept
inherited1052246623534; earlier prose calling themnonce0 waswrong. No prototype
nonce screen or officialbenchmark ran. Fullhashes/nativeevidence stayunchanged.
Finishedrmin wrapper explicitlydecodes/checks/removesold1052246623534 andappends
literalnew0; finalstream65447429/SF6f90ab4c, actualQ1233/proxy755806/113leases.
It is anungated intermediate, superseded bybetterresourceprofiles. Thebestwrapper
uses same checkednormalization, andfinalgate independentlyverifieszero tail.
See experiments/autorun-20261020-breakthrough/PROTOTYPE-TAIL-CORRECTION.md.

Strong square-depth/resource grid v1 preserves originalmissingcap faultfixture
andresumedleafsetup failures; neither became a gate. Correctedfault detects122
wrongoutputs/43phasefailures in128shots. V2adds onlytestfixturecap beforefreshSF,
passes34nativecontrols/fullcallerunits/fault, reproducesa871/dc1478. d12/d16
fullstreams actualQ1464/proxy746054/746007; square1536 andwalk1664 produceexact
dc1478, nogain. OR-of-measurement guardproxy canmispriceT; queuedfresh512x64
development measuresactualT/alloutputs againstcurrentofficial71 before selection.

Read-only output-value dependency audit v1 compilefailurepreserved; v2native4
passes capturedguards/SSA/RNG/conditionalreset/swap/fault checks. Public/T streams
retain22830/5260live measurement outputs andalmostallToffolis; no justified fast
filter/rejectionshortcut. No rewrittenquantum circuit ornonce screening occurred.
Originalpredictors remain non-certificates. Native/proxy counts never enterplots.

Cycle7 fourfronts203 andcycle8 sixfronts340 archive members verifylocally; sources,
patches,17protected hashes, alloriginalfailures andstreamhashes retained. Cycle9
collection continues. Lastlocalcheckpointb123a943; default-branchpush remains
blocked byautomaticapprovalreview pendingexplicituserpermission, no bypassretry.
Localwork/authorizedofficialuploads continue; useredits/submodules/serverjobs intact.

'''
for name in ['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;before=git('show','HEAD:'+name);blob=git('hash-object','-w','--stdin',data=prefix.encode()+before).decode().strip();git('update-index','--cacheinfo','100644',blob,name);p.write_bytes(prefix.encode()+p.read_bytes())
with(a/'LOG.md').open('a')as out:out.write('\n'+prefix)
helpers=['checkpoint-exact-drop-pipeline.py','CURRENT-ACTIVE.json','LOG.md','PROTOTYPE-TAIL-CORRECTION.md','prepare-public-prefix27-width-v2.py','prepare-public-width1233-deeper-context.py','prepare-public-width1233-development.py','prepare-public-expanded-cap.py','prepare-guarded-live-products.py','prepare-grouped-exact-resource-grid.py','resume-grouped-exact-resource-grid.py','prepare-grouped-exact-resource-grid-v2.py','prepare-public-drop-tradeoffs.py','prepare-public-drop-tradeoffs-v2.py','prepare-public-width1232-context.py','prepare-value-cone-audit.py','prepare-value-cone-audit-v2.py','value-cone-audit.rs','prepare-public-rmin-context.py','prepare-public-rmin-finished.py','prepare-public-best-drop-pipeline.py','prepare-public-best-drop-development.py','prepare-public-best-drop-final-gate.py','prepare-grouped-resource-development.py']
for cycle in[7,8,9]:helpers +=[f'prepare-cycle{cycle}-collection.py',f'seal-research-cycle{cycle}.py',f'collect-research-cycle{cycle}.py']
git('add','--',*[str((a/n).relative_to(root))for n in helpers])
directories=list(state['cycle7_verified_completed_evidence'])+list(state['cycle8_verified_completed_evidence'])+['breakthrough-public-expanded-cap-20261020','breakthrough-public-drop-tradeoffs-20261020','breakthrough-public-drop-tradeoffs-v2-20261020','breakthrough-public-rmin-context-20261020','breakthrough-public-rmin-finished-20261020','breakthrough-value-cone-audit-20261020','breakthrough-value-cone-audit-v2-20261020','breakthrough-grouped-exact-resource-grid-v2-20261020','breakthrough-grouped-resource-development-20261020','breakthrough-public-best-drop-context-20261020','breakthrough-public-best-drop-finished-20261020','breakthrough-public-best-drop-development-20261020','breakthrough-public-best-drop-final-gate-20261020']
git('add','--',*[str(Path('experiments')/n)for n in directories],'experiments/breakthrough-assessment-20261020/LATEST.json','experiments/breakthrough-assessment-20261020/snapshots/20261020T182525Z','experiments/breakthrough-assessment-20261020/snapshots/20261020T184845Z')
paths=git('diff','--cached','--name-only').decode().splitlines();assert all(x.startswith('experiments/')or x in['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']for x in paths);assert not any('resource-preflight'in x for x in paths);print(len(paths),'owned paths staged');print(git('diff','--cached','--shortstat').decode());print('Local checkpoint only; do not push without the pending explicit approval.')
