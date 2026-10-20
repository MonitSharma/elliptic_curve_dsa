import gzip,hashlib,json,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=a.parent;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
dirs=['breakthrough-global-semantic-component-20261020','breakthrough-semantic-lifetime-color-20261020','breakthrough-value-normalized-aig-v2-20261020','breakthrough-normalized-wrongpoint-check-20261020','breakthrough-de8-generic-repeat-v3-20261020','breakthrough-de8-generic-development-20261020']
excluded={'local-tool','candidate','prepared-source','target','__pycache__'}
for name in dirs:
 r=ex/name;(r/'.gitattributes').write_text('* -text\n');p=r/'.gitignore';prior=p.read_text()if p.exists()else''
 for line in ['local-tool/','candidate/','prepared-source/','__pycache__/','*.ops.bin','*.cnf','*.drat','*.jsonl','normalized-value-ir.bin.zst']:
  if line not in prior.splitlines():prior+=line+'\n'
 p.write_text(prior)
 for p in r.glob('*.jsonl'):p.with_suffix('.jsonl.gz').write_bytes(gzip.compress(p.read_bytes(),mtime=0))
 f=json.loads((r/'SOURCE-FREEZE.json').read_bytes())if(r/'SOURCE-FREEZE.json').exists()else{}
 names=f.get('tool_source_files',f.get('source_files',{}))
 if (r/'local-tool').is_dir()and names and all((r/'local-tool'/n).is_file()for n in names):
  assert all(sha(r/'local-tool'/n)==h for n,h in names.items())
  with tarfile.open(r/'preserved-tool-source.tar.gz','w:gz')as ar:
   for n in sorted(names):ar.add(r/'local-tool'/n,arcname=n,recursive=False)
  (r/'PRESERVED-TOOL-SOURCE.json').write_text(json.dumps({'files':names,'archive_sha256':sha(r/'preserved-tool-source.tar.gz')},indent=2)+'\n')
 files={}
 for p in r.rglob('*'):
  rel=p.relative_to(r)
  if any(x in excluded for x in rel.parts):continue
  if not p.is_file()or p.suffix in ['.cnf','.drat','.jsonl']or p.name.endswith('ops.bin')or p.name in ['normalized-value-ir.bin.zst','LOCAL-CHECKPOINT-MANIFEST.json']:continue
  assert p.stat().st_size<20_000_000,(name,rel,p.stat().st_size);files[rel.as_posix()]=sha(p)
 (r/'LOCAL-CHECKPOINT-MANIFEST.json').write_text(json.dumps({'files':files,'scope':'Completed source-bound verifier/component/development evidence only. No new benchmark or scored record. Original failures and checker exit/log distinction retained.'},indent=2)+'\n')
cert=json.loads((ex/'breakthrough-normalized-wrongpoint-check-20261020/RESULT.json').read_bytes());assert cert['constant_wrong_output_bits']==234 and cert['nonce_rejections']==0;assert(ex/'breakthrough-normalized-wrongpoint-check-20261020/TRIVIAL-CHECKER-QUALIFICATION.json').exists()
frozen=ex/'breakthrough-de8-repeat-finished-20261020';f=json.loads((frozen/'SOURCE-FREEZE.json').read_bytes());assert sha(frozen/'point-add-source.tar.gz')==f['source_archive_sha256']and sha(frozen/'source.patch')==f['source_patch_sha256'];assert all(sha(frozen/'prepared-source'/p)==h for p,h in f['source_files'].items())
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),global_product_goal_status='ACTIVE_UNFINISHED',active_jobs=[{'environment':'smu_server LHC-104-070 nohup','pid':3204403,'directory':'breakthrough-de8-repeat-finished-20261020','purpose':'Frozen source ddaa047c5c6f2ef4cd79d918c3f49b53ada81c22,206pointAdd/17protected. Native8PASS, official1.93generation running. Then freshfinished512development, sole32768x64finalgate cache-repeat-generic-final-20261020-v1 vs exactde8. ONLY PASS allows qualifiedascendingnonce1..65536/lowestpass, unchangedbenchmark; no upload before independentlocalevidence/currentrecord review. Do not restart or rerun a declared gate.'}],normalized_fixed_input_certificate=cert,checker_status_qualification='Zero-variable parse-time contradiction: official unchanged checker prints trivial UNSAT/s VERIFIED but returns1 because sts stays ERROR; source-pinned positive/negative controls reproduce exact branch. Complementary units normally VERIFIED/exit0; SAT invalidproof exit1/NOTVERIFIED. Earlier900sTIMEOUT remains unverified, no old verdict upgraded.',generic_repeat_development={'status':'DIAGNOSTIC_ONLY_512x64','parent_mean':746117.3225097656,'candidate_mean':746107.1288757324,'paired_delta':-10.193634033203125,'paired_se':2.3659088412059086,'identical_target_and_other_register_hashes':True,'parent_candidate_value_shots':[13,13],'phase_shots':[8,8],'dirty_shots':[0,0],'source_files':206,'protected_files':17,'stream_sha256':'9154237737f3624ead4a02a3f9d49260a27d37319c071bd98e25a654fdcd7de3'},exact_semantic_lifetime_result='Native7PASS/fullbothstreams complete, strongerproofs release morehelper lifetimes but peak unchanged1234/1464. No width record.',exact_semantic_action_result='Native12PASS/public1829 oneCCXtoCX (proxy0.5), de8 threezeroCCX (proxy3). Components only, no scored counts. Keep independent records separate.',next_product_front='Extend the qualified normalized-IR exact value proof to CURRENT public1829 and broader frozen fixtures; old6192 fixed-input certificate is not a production model. Strong lead: scalar AIG has only310CRNG nodes and all512outputs constant. Explore word-level exact Boolean interpretation to certify64inputs together, keeping unknown fallback and complete originalFS qualification mandatory before production nonce rejection. Numerical IR cache hash188c0947af7e7c6fb02bef415c26efd94209aeb873d500fc2cb8ecf872c56807 retained locally/ignored, source/scripts reproducible.')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
prefix='''## 21 October 2026: fixed-input value proof and final exact-cache pipeline

New verifier result on frozen OLD6192 source/first preserved failure only:
native29 and27 fullprotected value comparisons PASS. Complete exact semantic/
cofactor normalization makes scalarAIG only310nodes (all original CRNG atoms),
ALL512output literals constant.234bits disagree with protectedP+A reference.
CNF shrinks3,134,968variables/12,016,490clauses to ZEROvariables/234emptyclauses.
Independent syntactic contradiction checker/positive+SATnegative controls PASS.
0.070431857seconds scalarbuild. This is one source/input certificate, NOT a
general filter, a new statistical gate or a quantumresource record. No nonce
screened/rejected. NumericIR cache30,432,349bytes retained locally, SHA188c0947...

Unchanged DRAT checker also prints trivialUNSAT/sVERIFIED but returns1 because
parse-timeUNSAT leaves its sts=ERROR; pinned source and separate positive/
negative controls qualify that exact behavior. Contradictoryunits return0/
VERIFIED normally; SAT+invalidproof returns1/NOTVERIFIED. Original strict0report
kept; separate qualification explains branch. Initial overbroad exit assumption
failure retained. Earlier513MBproof/900sTIMEOUT remains UNCHECKED, not upgraded.

Exact semantic fullprefix native12: public1829 oneCCXtoCX/proxy0.5; de8 three
zeroCCX/proxy3. Stronger semantic lifetime color native7/fullbothparents passes
every logical/physical/phase/classical/RNG/executedcount control but peak stays
1234/1464 despite additional zero releases. These are component diagnostics.

Second2cache+repeatedgeneric source206/protected17 complete nonce0 stream915423,
canonicalcf941. Native guardedcache1PASS, prior independentproof9. Fresh paired
development512x64/8fullprotected batches each: means746117.3225097656 vs
746107.1288757324, delta-10.193634033203125 SE2.3659088412059086. Same13value and
8phase shots/12failedbatches, dirty0, NOtarget orother-registerhash differences.
These means are diagnostic, NOT scores. No READMEplot or officialupload.

Finished source parameterizes ONLY zero identity tail and must regenerate
EXACTsame frame. Server detached source ddaa047c5c6f2ef4cd79d918c3f49b53ada81c22,
native8PASS. nohupPID3204403 official1.93generation in progress. Then NEWfinished
512development, sole finalgate labelcache-repeat-generic-final-20261020-v1/
32768x64 versus exactde8; outcomeFINAL. OnlyPASS permits qualifiedascending
1..65536/lowestnonce and unchangedbenchmark. Independentlocal evidence/source/
freshpublicrecord review before authorized automatic GPT-6sol/Codex upload.
Global product goal ACTIVE; latest officialT still746114/Q1464/de8. Approved
41f769ec push completed; newer research commits remain local. Chemistry and
unrelated workloads untouched. No local longjobs remain at this checkpoint.
'''
for rel in ['docs/research-plan.md','docs/AGENT_HANDOFF.md']:
 p=root/rel;data=prefix.encode()+b'\n'
 if not p.read_bytes().startswith(data):p.write_bytes(data+p.read_bytes())
 blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+rel)).decode().strip();mode=git('ls-tree','HEAD','--',rel).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+rel],check=True)
with(a/'LOG.md').open('a',encoding='utf-8')as log:log.write('\n'+prefix+'\n')
scripts=['prepare-global-semantic-component.py','semantic-lifetime-color.rs','prepare-semantic-lifetime-color.py','prepare-de8-generic-development.py','prepare-de8-repeat-final-pipeline.py','run-de8-repeat-final-pipeline.py','launch-de8-repeat-pipeline.py','DE8-REPEAT-PIPELINE-TRANSFER.json','check-normalized-wrongpoint.py','prepare-normalized-wrongpoint-check.py','qualify-trivial-drat-status.py','qualify-trivial-drat-status-v2.py','checkpoint-normalized-proof-and-repeat.py','CURRENT-ACTIVE.json','LOG.md']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]
for name in ['breakthrough-de8-repeat-finished-20261020','breakthrough-de8-repeat-finished-development-20261020','breakthrough-de8-repeat-final-gate-20261020','breakthrough-de8-repeat-nonce-20261020','breakthrough-de8-repeat-final-20261020']:
 paths.extend(p.relative_to(root).as_posix()for p in(ex/name).iterdir()if p.is_file())
subprocess.run(['git','-C',str(root),'add','--',*paths],check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q+'/')for q in paths+['docs/research-plan.md','docs/AGENT_HANDOFF.md'])for p in staged);assert not any(any('/'+bad+'/'in p for bad in excluded)or p.endswith('ops.bin')or p.endswith('.cnf')or p.endswith('.drat')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve normalized fixed-input certificate and exact cache final pipeline'],check=True);print(git('rev-parse','HEAD').decode().strip())
