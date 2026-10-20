"""Independent source/receipt review and complete queue-only evidence bundle."""
import hashlib,json,os,re,shutil,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-public140-final-20261020';t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((r/'SOURCE-FREEZE.json').read_text());result=json.loads((r/'BENCHMARK-RESULT.json').read_text());search=ws/'breakthrough-public140-nonce-20261020';gate=ws/'breakthrough-public140-final-gate-20261020'
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
assert git('rev-parse','HEAD').decode().strip()==f['base']
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
for p in f['protected_files']:assert(t/p).read_bytes()==git('show','HEAD:'+p),p
assert result['qubits']==1464 and result['rounded_mean_executed_toffoli']==751182 and result['product']==1099730448
assert sha(t/'ops.bin')==result['native_receipt']['stream_sha256']=='dc6210044f475393b4c7901d6241bbd379a05a757ebaba1507acceab0c74966a'
assert json.loads((gate/'GATE-RESULT.json').read_text())['verdict']=='FAILURE_RATE_GATE_PASS'
assert sha(gate/'GATE-RESULT.json')==f['gate_result_sha256']
assert json.loads((search/'QUALIFICATION.json').read_text())['status']=='PASS'
rows=[json.loads(x)for x in(search/'production.jsonl').read_text().splitlines()];assert sorted(x['nonce']for x in rows)==list(range(1,129));assert[x['nonce']for x in rows if x['pass']]==[125]
assert sha(search/'production.jsonl')==f['search_result']['production_rows_sha256']
assert (t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
# Preserve exact blobs, bypassing line-ending filters, with all source bytes checked.
for p in sorted(f['source_files']):
 blob=git('hash-object','-w','--no-filters',p).decode().strip();git('update-index','--add','--cacheinfo','100644,'+blob+','+p);assert git('cat-file','blob',':'+p)==(t/p).read_bytes()
changed=git('diff','--cached','--name-only').decode().splitlines();assert changed and all(p.startswith('src/point_add/')for p in changed)
git('commit','-q','-m','Build fixed public140 uniform comparison candidate at nonce 125')
revision=git('rev-parse','HEAD').decode().strip();assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'))
review={'status':'COMPLETE_LOCAL_REPRODUCTION_REVIEW_PASS_QUEUED','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'native_receipt':result['native_receipt'],'protected_files_checked':17,'tracked_changes_only_point_add':True,'historical_results_restored':True,'nonce':125,'production_screens':128,'parallel_overrun_nonces':'126..128','partial_packet_control_nonces':'1..8, repeated in production; 24 protected full-state batches','selected_protected_replay':True,'unchanged_benchmark_passed_shots':9024,'failed_gate_reruns':0,'submission_mode':'queue','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete locally passing result targets independent Toffoli record. Not official, not global product record, not universal correctness or novelty proof.'}
(r/'FINAL-VERIFICATION.json').write_text(json.dumps(review,indent=2)+'\n')
note=f'''# Queued local Toffoli result: Q1464 / T751182

Complete unchanged benchmark passes all 9,024 shots: rounded mean executed
Toffolis **751,182**, actual mean 751181.5601728724, total 6,778,662,399.
Peak referenced logical qubits **1,464**, product **1,099,730,448**.
This improves the refreshed public Toffoli record 752,991 by 1,809 (0.24024%),
and uses 399 fewer qubits than its Q1863 parent. The public global product
939,138,168 is still lower. This is queued and has not been uploaded/evaluated.

AI model: **GPT-6 sol**. Coding harness: **Codex**. Research attribution:
MonitSharma. Inherited public arithmetic and prior postpasses are retained;
no independent novelty claim. Source revision `{revision}`, base `{f['base']}`.
Only `src/point_add/` differs; all 17 protected files remain byte-identical.
Frozen fixed public 140-row schedule, uniform +2 comparison precision,
plain allocator with zero-operation clean-pool priming, and generic exact
postpasses. Source-bound/census cuts and old frozen late cache are omitted.
The independent Q692 width evidence and all previous gate verdicts stand.

Final statistical gate declared before running: label
`public140-uniform2-generic-final-20261020-v1`, 32,768 batches of 64 shots
(2,097,152 shots per source), exact public Toffoli parent 62341149 stream
`09dbeacbd80a5d51656723c4350e367e91d5b5a00306008bf97b288bd4a205e4`.
Frozen candidate nonce0 stream
`a85c3ffa0ec725b04900ac79d5729dab126a870d566533f53d0f256c0d90cf98`.
Parent/candidate: wrong-value shots 1212/1190, phase shots 816/663,
dirty shots 0/0, failing batches 1379/1230. Candidate failed batches per
9,024-shot packet 5.29266357421875. Paired batch discordance b=63 newly
failing, c=212 newly passing, exact one-sided McNemar P(X>=63|n=275,p=.5)
passes 0.05 (float rounds to 1.0). All four gate requirements pass.
Wrong-value IDs are not identical: 15 newly wrong and 37 newly correct.
No gate rerun, relabel, extension or re-judging was performed.

Frozen arithmetic was screened in ascending order from 1, selecting the
lowest passing **nonce 125**, without Toffoli-based selection. All **128**
production nonces 1..128 are recorded; 126..128 are window overrun and only
125 passes. Partial-packet controls on nonces 1..8 are additional and repeat
those eight production nonces: 24 full qubit/classical/phase/RNG-state
comparisons at batches 0,70,140 with protected scalar simulation and curve
references, plus partial-mask controls. The selected complete packet also
passed protected run_tests and the unchanged benchmark. Simulator statistics
were not used for selection. Initial launcher failed before any screening
because cargo was absent from PATH; corrected absolute-path runner retained.

The selected source changes only the 48-bit identity-tail nonce constant.
All pre-tail operation records are byte-identical to the gated nonce0 stream.
Final native stream SHA256:
`dc6210044f475393b4c7901d6241bbd379a05a757ebaba1507acceab0c74966a`.
Operation record SHA256:
`facba5d70a92ee136e0e805efb2392866d9f2e1aa7917706e86134b3a13ac958`.
Inherited approximate arithmetic remains. Finite-packet success and the
disclosed passing gate do not establish universal point-add correctness.
'''
(r/'SUBMISSION-NOTE.md').write_text(note)
# Full gate/nonce tool sources and raw census/search rows accompany final source.
for label,origin in [('nonce-evidence',search),('gate-evidence',gate)]:
 dest=r/label;dest.mkdir()
 for current,dirs,names in os.walk(origin):
  dirs[:]=[d for d in dirs if d not in ['target','__pycache__']]
  for n in names:
   p=Path(current)/n
   if 'resource-preflight'in n or n in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:continue
   out=dest/p.relative_to(origin);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
files=[]
for current,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in ['candidate','__pycache__'])
 for n in sorted(names):
  p=Path(current)/n
  if 'resource-preflight'in n or n in ['final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:continue
  files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'review':review},indent=2)+'\n')
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as a:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'final-evidence.tar.gz'),'archive_bytes':(r/'final-evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(json.dumps(review))
