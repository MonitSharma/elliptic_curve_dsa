import hashlib,json,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=a.parent;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
dirs=['breakthrough-quantum-sharing-profile-20261021','breakthrough-peak-rematerialization-audit-20261021','breakthrough-multicap-rematerialization-20261021','breakthrough-polynomial-rematerialization-20261021','breakthrough-flat-guard-control-20261021','breakthrough-merged-loan-audit-20261021','breakthrough-public-polynomial-borrow-20261021','breakthrough-compact-current-product-anf-20261021','breakthrough-compact-census-shadow-20261021','breakthrough-original-fs-reference-20261021']
excluded={'local-tool','candidate','target','__pycache__'}
for name in dirs:
 r=ex/name
 if name!='breakthrough-original-fs-reference-20261021':assert(r/'run.exit').read_text().strip()=='0',name
 if(r/'SOURCE-FREEZE.json').exists():
  f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());names=f.get('tool_source_files',f.get('source_files',{}));assert all(sha(r/'local-tool'/n)==h for n,h in names.items());arpath=r/'preserved-tool-source.tar.gz'
  if not arpath.exists():
   with tarfile.open(arpath,'w:gz')as ar:
    for n in sorted(names):ar.add(r/'local-tool'/n,arcname=n,recursive=False)
  with tarfile.open(arpath)as ar:
   assert {m.name for m in ar.getmembers()}==set(names)
   for m in ar.getmembers():assert m.isfile()and hashlib.sha256(ar.extractfile(m).read()).hexdigest()==names[m.name]
  (r/'PRESERVED-TOOL-SOURCE.json').write_text(json.dumps({'files':names,'archive_sha256':sha(arpath)},indent=2)+'\n')
 files={}
 for p in r.rglob('*'):
  rel=p.relative_to(r)
  if any(x in excluded for x in rel.parts):continue
  if not p.is_file()or p.name.endswith('ops.bin')or p.name=='LOCAL-CHECKPOINT-MANIFEST.json':continue
  assert p.stat().st_size<20_000_000,(name,rel);files[rel.as_posix()]=sha(p)
 (r/'LOCAL-CHECKPOINT-MANIFEST.json').write_text(json.dumps({'files':files,'scope':'Completed source-bound proof/control/plan evidence, or explicitly unexecuted fixed replay declaration. No new achieved resource, final gate, benchmark, nonce search or official submission.'},indent=2)+'\n')
compact=json.loads((ex/'breakthrough-compact-census-shadow-20261021/RESULT.json').read_bytes());assert compact['shadow']['fully_known_output_shots']==32768 and compact['shadow']['certified_wrong_shots']==54 and compact['nonce_rejections']==0
flat=json.loads((ex/'breakthrough-flat-guard-control-20261021/RESULT.json').read_bytes());assert flat['qualification']['protected_fullstream_comparisons']==24
poly=json.loads((ex/'breakthrough-polynomial-rematerialization-20261021/RESULT.json').read_bytes());merged=json.loads((ex/'breakthrough-merged-loan-audit-20261021/RESULT.json').read_bytes());public=json.loads((ex/'breakthrough-public-polynomial-borrow-20261021/RESULT.json').read_bytes());assert public['unproved_regions']==450 and not public['all_regions_covered']
ref=json.loads((ex/'breakthrough-original-fs-reference-20261021/REFERENCE-DECLARATION.json').read_bytes());assert ref['status']=='FIXED_EXISTING_CONTROL_REPLAY_DECLARED_NOT_EXECUTED'
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),active_jobs=[],global_product_goal_status='ACTIVE_UNFINISHED',next_product_front='OriginalFS fixed-control membership/certificate qualification on already-screened OLD6192 controls1..8 ONLY. Compact backend now native40/fresh33 and native42/fresh24+all32768storedtargethashesPASS. Preserve oldEXHAUSTED1..65536, never resume. Actual qualified originalscreen model=(), advisoryhitfalse; no production rejection shortcut yet. After transcript qualification build advisorynominator+exactpackedfailureproof with mandatory fullstate fallback. PubliconeCCXtoCX development saving-.49945 remains COMPONENT ONLY, needs finished literal source/currentrecordrefresh/sole finalgate/qualified search/unchangedbenchmark before upload.',rematerialization_plans={'status':'READ_ONLY_NOT_ACHIEVED_Q_OR_T','scalar_cap1463':{'covered':True,'extra_T_upper_bound':32,'regions':16},'polynomial_term_limit':8,'complete_cases':[{k:c[k]for k in ['cap','regions','extra_executed_toffoli_per_shot_upper_bound']}for c in poly['cases']if c['all_regions_covered']],'merged_cases':merged['cases'],'public_cap1233':{'covered':False,'unproved_regions':450,'regions':len(public['regions']),'complete_extra_T_bound':None},'scope':'Wide plans cover32fewer slots but current cost/holes do not beat globalproduct; no allocator/candidate/gate/nonce/benchmark. No projected counts in READMEplots.'},guard_flatten_control={'status':'COMPLETE_PASS_NO_RESOURCE_IMPROVEMENT','native':5,'full_protected_comparisons':24,'emitted_operations':flat['stats']['emitted_operations'],'stream_sha256':flat['output_sha256'],'scope':'All physical quantum/original classical bits, phase, executedT/Cliffordcounts and RNG words identical on24fresh arbitrary-input comparisons. Original metadata/measurementorder unchanged. Reusable prerequisite only.'},compact_backend={'status':'CURRENT_PARENT_VERIFIER_QUALIFICATION_COMPLETE_NO_PRODUCTION_REJECTION','native_fixture_tests':40,'fixture_full_protected_comparisons':33,'fixtures':192,'fixture_times_seconds':[.069266135,.062077742,.065517342],'broad_native_tests':42,'broad_fresh_full_protected_arbitrary_comparisons':24,'preserved_census_shots':32768,'fully_known_outputs':32768,'certified_value_failures':54,'false_rejections':0,'unknown_outputs':0,'target_hash_mismatches':0,'broad_seconds':63.534927826,'previous_broad_seconds':106.727310831,'nonce_screens':0,'nonce_rejections':0},original_FS_fixed_replay_reference=ref,new_official_summary='No newofficialresult thiscycle. Priorofficialffe20 Q1464/T746112 remains T minimum in latest00:40UTC1717snapshot; product1829 Q1234/T755314/932057476, width669. Globalproduct goal ACTIVE. Exact approved41f769ec pushed previously; newercommits remain local.')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
addition='''## 21 October 2026: compact exact verifier and reversible peak plans

No new benchmark/finalgate/nonce screen/official submission. Globalproduct goal
ACTIVE; latest00:40UTC1717snapshot has priorofficialffe20 Q1464/T746112,
globalproduct1829 Q1234/T755314/932057476, width669. PreserveQ692 evidence.

Compact verifier storage native40/fresh33protected on192fixedpointsPASS:
all128wrong certified,64passingcontrols unrejected, all512outputbitsknown.
Fixed proof times .069266135/.062077742/.065517342sec/64 vs .132..153prior.
Broader native42/fresh24protected+ALL32768preserved currentpublic targethashes
PASS; all54value failures certified, unknown0,false rejection0,mismatch0.
63.534927826sec vs106.727310831previous includingpointgeneration. No new census,
no pastgate rejudged, no nonce screened/rejected. Full-key immutable coefficient
forms, old qualifiedalgebra unchanged;8totalterms/degree4/caches preserved,
1mform budget has soundTVfallback. This is verifierresearch, not a quantumscore.

Read-only quantum sharing native5/fullbothparents has NO peakduplicate margin:
distinctfunctionpeak1234/1464, conservativecopyprojection1235/1464. Retired.
Exactpeakrematerialization native5 covers all16wide-parent1463-cap islands with
at most32extraT/shot, but not an emitted allocation. Scalar multicapnative7
fails deeper; XOR8termrecipesnative10 fully cover1462/1460/1456/1448/1432caps
with raw worstcase addedT80/244/552/1712/6144. Exact adjacent idleloan merge
native2 reduces these to48/178/476/1572/5870. Deeper plans incomplete with NULL
completebounds; currentproductcap1233 port has450unproved of3007regions.
These costs/holes do not beatglobalproduct. No actualQ/T, allocator, candidate,
gate or nonce; never display these plans in READMEresultsplots.

Guard flattening prerequisite native5+24COMPLETEprotected comparisonsPASS.
Allphysicalqubits/originalclassicalbits, absolutephase, executedT/Cliffordcounts
and every originalRNGword match. Currentffe20 input9185 -> control735f063c,
10995456->11292508ops, no newquantumgate/measurement. OriginalPush snapshots
captured beforebitmutation; originalmetadata unchanged. No resourceimprovement.

OriginalFSreference declared for SAME already-screened OLD6192controls1..8 and
each recorded badbatch7/3/5/5/4/1/0/29 (nonce7phaseonly). Replay NOT started.
Qualifiedenginebinary8e436f matchesolddeclaration. Protectedfiat_shamir_seed
function byteidentical to engine; exacttailcode/source hashespreserved.
Retired1..65536EXHAUSTED verdict final; neverresume/extend. Newqualification
must bindOLDcache independently, checkactual9024attempt/skip membership and
fullseed/prefixseed equality before exactwrongpoint certificates. No heuristic
mayreject; qualified oldengine hasmodel=(),advisoryhitfalse, exactfullstateonly.
Futurecandidate stillneeds own frozen passedgate and originalFS qualification.

Alljobs in thiscycle finished; next work is ORIGINAL_FS fixed-control audit,
then advisorynomination plus exactpackedproof/fullstatefallback. Public exact
singleCCXtoCX still componentonly. Exact approved41f769ec push completed earlier;
newercommits local. Preexisting edits/chemistry/unrelatedHPC jobs preserved.

'''
for rel in ['docs/research-plan.md','docs/AGENT_HANDOFF.md']:
 p=root/rel;data=addition.encode()
 if not p.read_bytes().startswith(data):p.write_bytes(data+p.read_bytes())
 blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+rel)).decode().strip();mode=git('ls-tree','HEAD','--',rel).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+rel],check=True)
with(a/'LOG.md').open('a',encoding='utf-8')as log:log.write('\n'+addition)
scripts=['peak-rematerialization-audit.rs','prepare-peak-rematerialization-audit.py','prepare-multicap-rematerialization.py','polynomial-rematerialization.rs','prepare-polynomial-rematerialization.py','flatten-captured-guards.rs','prepare-flat-guard-control.py','merge-rematerialization-plans.rs','prepare-merged-loan-audit.py','prepare-public-polynomial-borrow.py','compact-anf-values.rs','prepare-compact-anf-values.py','prepare-compact-census-shadow.py','declare-original-fs-fixed-reference.py','checkpoint-rematerialization-and-compact-proof.py','CURRENT-ACTIVE.json','LOG.md']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts];subprocess.run(['git','-C',str(root),'add','--',*paths],check=True);staged=git('diff','--cached','--name-only').decode().splitlines();allowed=paths+['docs/research-plan.md','docs/AGENT_HANDOFF.md'];assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged);assert not any('/local-tool/'in p or p.endswith('ops.bin')or p.endswith('.jsonl')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve compact exact verifier and source-bound reversible workspace plans'],check=True);print(git('rev-parse','HEAD').decode().strip())
