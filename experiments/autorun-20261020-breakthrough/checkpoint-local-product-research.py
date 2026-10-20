import gzip,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=root/'experiments';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
dev=ex/'breakthrough-public1829-local-development-v2-20261020';assert(dev/'controller.exit').read_text().strip()=='0';d=json.loads((dev/'DIAGNOSTIC.json').read_bytes());assert all(v['dirty_shots']==0 for v in d['summaries'].values());assert all(not v['new_value_failing_shots']and not v['new_value_passing_shots']for v in d['comparisons'].values())
retired={'status':'DEVELOPMENT_RESOURCE_FRONT_NONCOMPETITIVE_NO_FINAL_GATE_OR_NONCE','mean_executed_toffoli':{k:v['mean_executed_stream_toffoli']for k,v in d['summaries'].items()},'cap1233_product_record_toffoli_threshold':932057476/1233,'cap1233_development_excess_toffoli':d['summaries']['cap1233']['mean_executed_stream_toffoli']-932057476/1233,'source_freeze_sha256':sha((dev/'SOURCE-FREEZE.json').read_bytes()),'diagnostic_sha256':sha((dev/'DIAGNOSTIC.json').read_bytes()),'scope':'512x64 development means only, not scored counts or full benchmark. Both prototypes cost too much for current product record. Same54value failing shots, zero dirty; cap1233 differs on18 jointlybad target lanes, no other-register differences. Preserve all outcomes; no gate/nonce/benchmark/upload.'};(dev/'RESOURCE-STATUS.json').write_text(json.dumps(retired,indent=2)+'\n')
dirs=['breakthrough-local-product-filter-replay-20261020','breakthrough-value-curve-audit-v2-20261020','breakthrough-value-affine-audit-v3-20261020','breakthrough-value-output-invariance-audit-20261020','breakthrough-value-aig-audit-20261020','breakthrough-value-aig-cnf-qualification-20261020','breakthrough-public1829-width-port-local-v2-20261020','breakthrough-public1829-width-port-local-v3-20261020','breakthrough-public1829-width-port-local-v4-20261020','breakthrough-public1829-local-development-20261020','breakthrough-public1829-local-development-v2-20261020','breakthrough-public1829-context-audit-20261020','breakthrough-public1829-lifetime-audit-20261020','breakthrough-sat-proof-tools-20261020','breakthrough-sat-proof-tools-v2-20261020','breakthrough-sat-proof-tools-v3-20261020','breakthrough-sat-proof-tools-v4-20261020']
for name in dirs:
 r=ex/name;(r/'.gitattributes').write_text('* -text\n')
 for p in r.glob('*.jsonl'):
  if p.stat().st_size>1000000:p.with_suffix(p.suffix+'.gz').write_bytes(gzip.compress(p.read_bytes(),mtime=0))
 p=r/'.gitignore';s=p.read_text()if p.exists()else''
 for line in ['local-tool/','local-protected/','tool-repos/','observer/','candidate/','stats-tool/target/','*.jsonl','*.cnf','*.drat','*resource-preflight*']:
  if line not in s.splitlines():s+=line+'\n'
 p.write_text(s)
 files={p.relative_to(r).as_posix():sha(p.read_bytes())for p in r.rglob('*')if not any(part in ['local-tool','local-protected','tool-repos','observer','candidate','target']for part in p.relative_to(r).parts)and p.is_file()and p.suffix not in ['.jsonl','.cnf','.drat']and p.name!='LOCAL-CHECKPOINT-MANIFEST.json'};(r/'LOCAL-CHECKPOINT-MANIFEST.json').write_text(json.dumps({'status':'OWNED_COMPLETED_OR_EXPLICITLY_UNLAUNCHED_RESEARCH_CHECKPOINT','files':files,'scope':'Saved research source/evidence only. No diagnostic count is a quantum record; failed tools/fixtures retained as failures.'},indent=2)+'\n')
assessment=ex/'breakthrough-assessment-20261020';snap=assessment/json.loads((assessment/'LATEST.json').read_bytes())['snapshot'];records=json.loads((snap/'PUBLIC-RECORDS.json').read_bytes());raw=(snap/'public-submissions.json').read_bytes();(snap/'public-submissions.json.gz').write_bytes(gzip.compress(raw,mtime=0));names=['PUBLIC-RECORDS.json','leader-product.json','leader-qubits.json','leader-toffoli.json','public-submissions.json.gz'];(snap/'SNAPSHOT-MANIFEST.json').write_text(json.dumps({'raw_api_sha256':sha(raw),'files':{n:sha((snap/n).read_bytes())for n in names},'scope':'Fresh21:49UTC1716official records unchanged: product1829, width669/1df8, our T746114/de8.'},indent=2)+'\n');(snap/'.gitattributes').write_text('* -text\n')
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),latest_public_snapshot=snap.relative_to(root).as_posix(),public_product=records['leaders']['product'],public_width=records['leaders']['qubits'],new_product_resource_development=retired,active_jobs=[{'environment':'Windows hidden foreground WSL client','pid':23564,'directory':'breakthrough-sat-proof-tools-v5-20261020','purpose':'Same first fixed-source Boolean CNF. Core716SATtests pass in predecessor; DRAT checker build fixed with_DEFAULT_SOURCE macro. Require independent valid/invalid proof controls and checked proof. Earlier detached v5 launch died before freeze/computation; foreground client keeps WSL alive.'},{'environment':'remote last known','pid':3143340,'directory':'breakthrough-value-boolean-reset-audit-20261020','purpose':'Native17PASS before SSH outage; finalstatus unknown. Do not restart/assume completion until reconnected.'}],next_product_front='Current public1829 exact workspace/caches prototypes both noncompetitive by complete development; no finalgate ornonce. Lifetime-only audit no width gain. Pursue stronger exact classical-guard semantic normalization and typed value proofs to accelerate high-failure search; prooftools on same frozen oldinput are research only. Automatically submit each complete verified current-record improvement asGPT6sol/Codex.',completed_local_verifier_fronts={'guard_fusion':'Native20/24protected finalvalue comparisons PASS,321rounds/liveRNG5690;8arbitraryfixtures zero knownbits. No nonce rejection.','valid_curve':'Native21/120protected comparisons (24arbitrary+96validcurve),32x64fixed fixtures all zero knownbits. No false certificate.','bounded_anf_v3':'Native24/30protected comparisons; both cases finish with8491429/8479961monomials; zero known/certifiedwrong bits. Earlier2m/8m budgets inconclusive, all sources preserved.','output_invariance':'Native21/30protected comparisons, same128preserved failures allwrong under3patterns; all32768output bits identical across3patterns onbothbatches. DIAGNOSTIC ONLY, never proof.','Boolean_AIG':'Native23/27protected comparisons; first fixedoldfailure only,3881075DAG nodes,3134968CNFvars/12016490clauses,0constantwrongbits,0.550112193secbuild. Encoder additionally exhaustivelychecked24native. Z3 CNFparsehits2GiBcap,inconclusive. No nonce rejected.','SAT_tools':'Rootpermission/fullCLI signal-timing failures preserved acrossv1/v2/v3. v4 core716solving/kitten testsPASS; DRATstrictC99featuremacrocompilefailure preserved. v5 explicit_DEFAULT_SOURCE macro, independent valid/invalid proof controls required, proofproducer untrusted; no fullsuitepass claimed.'},global_product_goal_status='ACTIVE_UNFINISHED')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
prefix='''## 21 October 2026: complete local product development; exact proof research

Fresh21:49UTC1716publicrecords unchanged: our officialde8 Q1464/T746114 remains
independentT minimum; globalproduct1829 Q1234/T755314/932057476, width669/1df8.
Global product goal ACTIVE. No new benchmark, finalgate, nonce or submission.

Portable local public1829 exactworkspace gridV4 complete, native9PASS, public
stream16567 byteexact. FailedV2 variants stopped at protected source-table hash
checks because clear_process_env removed the selector; original failures saved.
V4 passes explicitbool, never changes/disables bindings; publicfalse path exact.
IntermediateV3 adapter setup stopped before native/input tests; preserved.
Fresh existingwire context proofs native9PASS:115leases atQ1234,114atQ1233,
zero added wires; old public tables never transported. Lifetime/color read-only
audit finds no extra width gain on any of the3streams, not an emitted candidate.

Actual development public1829-workspace-cache-local-avx2-development-20261020-v1,
512x64/source,2workers/8fullprotected scalarbatches each: parent755308.7080383301,
cachedQ1234 755341.0234680176, cachedQ1233 756053.1765136719. DIAGNOSTIC means,
NOT scores. Bothnoncompetitive; Q1233needs <=755926.5823195,~126.6T lower.
All54valuefail shots sameIDs/dirty0; phase42/40/41; failedbatches63/65/63;
Q1233 has18target differences ONLY on jointlybad values, nootherregisterdiff.
No finalgate/nonce/benchmark/upload for theseprototypes. Preserve every mismatch.
LocalAVX512 predecessor NOTLAUNCHED (host12700K hasAVX2/noAVX512 andnoremote libs).
PortableAVX2 twohalves/eightword ABI passes3072basis/RNGlanes with EVERY protected
wire/bit/phase/RNG/T; originalcompactcontrol alsoPASS. Protected Rust curve/SHAKE
replace externalserverlibraries. All17protected bytes unchanged.

Guardfusion native20/24wholevalue controlsPASS,321rounds reduce liveRNG to5690;
no knownoutputbits on8arbitraryfixtures. New validcurve audit native21 and120
wholeprotected comparisons passes,32fixed64shot validcurve fixtures also zero
knownbits. BoundedANFv3 native24/30controls finishes~8.49mmonomials, no certificate;
earlier2m/8m budget misses preserved. Same128oldfailure fixtures wrongunderall3
patterns and EVERY sampledoutputbit invariant; sample invariance isNOTa proof.

ExactscalarBoolean AIG on FIRST frozen oldfailure:3881075nodes,3134968CNFvars,
12016490clauses;0.550112193secbuild. Native23/27wholeprotected controlsPASS;
actual signedCNF encoder additionally exhaustive24native controls. Z3parse2GiB
limit hitsOOM, INCONCLUSIVE; no wrongpoint certificate ornonce use. Isolated
officialKissat/DRATsources frozen witharchives/wholehashes. Fullsuitefailures
rootpermissions andtoo-fastSIGINTtiming retained, never claimedpass. Solving/
kitten716tests PASS; DRATstrictC99build failed missing_DEFAULT_SOURCE, separate
V5 compilesunchanged checkerwiththatfeaturemacro. Require independent valid/
invalidproof controls and VERIFIED DRAT before any proofclaim. Source/input
unchanged, no gateverdict rerun. V5 early detachedWSL launch died BEFORE any
freeze/computation; Windows hiddenforeground WSLclient23564 nowholdsjobalive.
Use a foregroundclient forfuture local longjobs; detachedWSL shell mayterminate.

SSH smu_server remains unreachable; remoteBoolean audit3143340 lastnative17PASS,
finalstatus unknown. No remotejob stopped orrestarted. Chemistry untouched.
Defaultbranchpush remains blocked byautomaticapprovalreview pending explicit
approval; no bypass. Allowned evidence savedlocally, user edits preserved.
'''
for path in ['docs/research-plan.md','docs/AGENT_HANDOFF.md']:
 p=root/path;data=prefix.encode()+b'\n';p.write_bytes(data+p.read_bytes());blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+path)).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
scripts=['CURRENT-ACTIVE.json','checkpoint-local-product-research.py','prepare-public1829-width-port-v2.py','prepare-local-public1829-port-v3.py','prepare-local-public1829-port-v4.py','prepare-value-affine-audit-v3.py','value-affine-audit-v3.rs','prepare-value-output-invariance-audit.py','value-aig-audit.rs','prepare-value-aig-audit.py','prepare-aig-cnf-qualification.py','solve-value-aig.py','launch-value-aig-solver.py','prepare-sat-proof-tools.py','run-sat-proof-tools.py','prepare-sat-proof-tools-v2.py','run-sat-proof-tools-v2.py','prepare-sat-proof-tools-v3.py','run-sat-proof-tools-v3.py','prepare-sat-proof-tools-v4.py','run-sat-proof-tools-v4.py','prepare-sat-proof-tools-v5.py','run-sat-proof-tools-v5.py','prepare-public1829-lifetime-audit.py','prepare-public1829-context-audit.py','prepare-local-public1829-development.py','prepare-local-public1829-development-v2.py','local-avx2-observer-tests.rs']
active=ex/'breakthrough-sat-proof-tools-v5-20261020';activepaths=[p.relative_to(root).as_posix()for p in active.iterdir()if p.is_file()and p.name in ['.gitignore','.gitattributes','PLAN.md','run.py','run-local.sh','launch-local.sh','foreground-windows.pid']]
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+activepaths+[snap.relative_to(root).as_posix(),'experiments/breakthrough-assessment-20261020/LATEST.json']
subprocess.run(['git','-C',str(root),'add','--',*paths,':!**/public-submissions.json'],check=True);staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q+'/')for q in paths+['docs/research-plan.md','docs/AGENT_HANDOFF.md'])for p in staged);assert not any(any('/'+bad+'/'in p for bad in ['candidate','observer','local-tool','local-protected','tool-repos','target'])or p.endswith('ops.bin')or p.endswith('.cnf')or p.endswith('.drat')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve full local product development and exact proof research outcomes'],check=True);print(git('rev-parse','HEAD').decode().strip())
