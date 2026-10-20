"""Review, commit exact source blobs and queue the complete new local result."""
import hashlib,json,os,shutil,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-public140-exact154-final-20261020';t=r/'candidate';old=ws/'breakthrough-public140-exact154-20261020';gate=ws/'breakthrough-public140-exact154-final-gate-20261020';search=ws/'breakthrough-public140-exact154-nonce-20261020';engine=ws/'breakthrough-public140-nonce-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists();f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());g=json.loads((gate/'GATE-RESULT.json').read_text());sr=json.loads((search/'SEARCH-RESULT.json').read_text());public=json.loads((r/'PUBLIC-RECORDS.json').read_text());assert b['qubits']==1464 and b['rounded_mean_executed_toffoli']==751027 and b['product']==1099503528
assert git('rev-parse','HEAD').decode().strip()==f['base']=='d45e76b3592a82f47c9fd3ef60741eb8c78caf7c';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert len(f['source_files'])==194 and len(f['protected_files'])==17
for p in f['protected_files']:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='public140-exact154-final-20261020-v1';assert g['candidate_source_freeze_sha256']==sha(old/'SOURCE-FREEZE.json');assert g['candidate_stream_sha256']=='7b165a67d95bdfadc274ddf303bf7a092c63d1d42bf223510e81d628be88fb3e';assert f['gate_result_sha256']==sha(gate/'GATE-RESULT.json')
assert sha(t/'ops.bin')==b['native_receipt']['stream_sha256']=='77d43b25b1526603b8e496da5f514a1b397a849bdd6eb9511e11beb0536e3057';assert b['native_receipt']['pre_tail_byte_identical_to_gated_source'];rows=[json.loads(x)for x in(search/'production.jsonl').read_text().splitlines()];assert sorted(x['nonce']for x in rows)==list(range(1,257))and sorted(x['nonce']for x in rows if x['pass'])==[209];assert sr['selected_nonce']==209 and sr['production_screens']==256 and sha(search/'production.jsonl')==sr['production_rows_sha256'];assert json.loads((search/'QUALIFICATION.json').read_text())['status']=='PASS';assert(t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
for p in sorted(f['source_files']):
 blob=git('hash-object','-w','--no-filters',p).decode().strip();git('update-index','--add','--cacheinfo','100644,'+blob+','+p);assert git('cat-file','blob',':'+p)==(t/p).read_bytes()
changed=git('diff','--cached','--name-only').decode().splitlines();assert changed and all(p.startswith('src/point_add/')for p in changed);git('commit','-q','-m','Apply 154 exact product leases on fixed public140 source at nonce 209');revision=git('rev-parse','HEAD').decode().strip();assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'))
public_t=public['leaders']['toffoli'];review={'status':'COMPLETE_LOCAL_REPRODUCTION_REVIEW_PASS_QUEUED','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':194,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'nonce':209,'production_screens':256,'parallel_overrun':'210..256','partial_packet_control_nonces':'1..8 repeated in production,24 full-state scalar batches','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'public_refresh_at_utc':public['at_utc'],'public_toffoli_parent':public_t,'beats_refreshed_public_t':751027<public_t['officialMetrics']['toffoli'],'submission_mode':'queue','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete local benchmark improves the independent T objective; not officially evaluated and not a global product record. Every earlier gate verdict and the independently official4045 result remain unchanged.'};(r/'FINAL-VERIFICATION.json').write_text(json.dumps(review,indent=2)+'\n')
note=f'''# Queued exact154 local result: Q1464 / T751027

The unchanged complete benchmark passes all9,024 shots: **1,464 logical
qubits**, **751,027 rounded mean executed Toffolis**, actual mean
751027.0876551418, total6,777,268,439. Product **1,099,503,528**.
Relative to current official Toffoli parent4045 (Q1464/T751182), this saves
**155 rounded Toffolis** at identical width. The independent global product
939,138,168 remains lower. This candidate is **queued, not uploaded or
officially evaluated**. Public records were refreshed at {public['at_utc']}.

AI model recorded for this research: **GPT-6 sol**; coding harness: **Codex**.
Research attribution: MonitSharma. Source revision `{revision}`, based on
public parent `{f['base']}`. Only src/point_add/ differs; all17 protected
tracked files and historical results remain byte-identical. Inherited public
arithmetic and prior passes are attributed in the source; no independent
novelty or universal correctness claim. Q692 evidence and all old verdicts stand.

The sole circuit change is154 unconditional product leases, nominated from
stream fingerprints and individually accepted by full exact arbitrary-cut
algebra with arbitrary data/classical values/measurement outcomes. Existing
zero donors, conservative no-touch/nonoverlap checks and HMR/CZ repair are
used. Although the research tool permitted16 additional donors, none increases
the final referenced width. A separate64-donor run produced the identical
stream. Complete native generation reproduces every proved operation record.
The initial research runner's framed-hash assertion failed because the
diagnostic writer sets zstd window_log27 and the protected writer uses its
default; original failure retained. No source or circuit change/rerun was
made for the correction. Native27 controls and canonical record equality pass.

This independent finished source passed its **own** predeclared final gate,
label `public140-exact154-final-20261020-v1`,32,768 batches x64 shots per
source (2,097,152 each). Parent is exact official4045 stream
`dc6210044f475393b4c7901d6241bbd379a05a757ebaba1507acceab0c74966a`;
frozen candidate nonce0 stream
`7b165a67d95bdfadc274ddf303bf7a092c63d1d42bf223510e81d628be88fb3e`.
Wrong-value shots1162/1162 with **identical failing shot IDs**, phase shots
668/634, dirty shots0/0, failed batches1193/1200 (parent/candidate).
Candidate failed batches per9,024-shot packet5.16357421875. Paired exact
McNemar b22/c15, one-sided p0.1620043000439182, meets0.05. The seven additional
failed batches are disclosed; all four predeclared requirements pass. The
gate is final and was never rerun, extended, relabelled or re-judged. The
earlier uniform2 gate was not reused for this circuit.

After that pass, frozen arithmetic was screened ascending from1. **Nonce209**
is the lowest pass among **256** production screens1..256, and the sole pass;
210..256 are disclosed window overrun. Additional partial-packet controls on
nonces1..8 repeat those production nonces:24 protected full qubit/classical/
phase/RNG comparisons at batches0,70,140 with scalar curve checks and partial
masks. The selected complete packet additionally passed protected run_tests
and the unchanged benchmark. No arithmetic filters, packet-content tuning or
Toffoli-based nonce selection. Only the nonce literal changes from gated
source; every pre-tail record is byte-identical.

Selected native stream SHA256
`77d43b25b1526603b8e496da5f514a1b397a849bdd6eb9511e11beb0536e3057`;
operation records SHA256
`00db935f7eb19d41e6d5b0dd160ece02c5ce397d8aa710e64da5cdef46255fb2`.
Inherited approximate arithmetic remains. Finite packet success and the
disclosed statistical pass do not establish correctness on all point inputs.
''';assert not(r/'SUBMISSION-NOTE.md').exists();(r/'SUBMISSION-NOTE.md').write_text(note)
for label,origin in [('nonce-evidence',search),('gate-evidence',gate),('prover-evidence',ws/'breakthrough-public140-cache-20261020')]:
 dest=r/label;dest.mkdir()
 for current,dirs,names in os.walk(origin):
  dirs[:]=[d for d in dirs if d not in ['target','__pycache__']]
  for n in names:
   p=Path(current)/n
   if 'resource-preflight'in n or n=='ops.bin'or n.endswith('.ops.bin')or n in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:continue
   out=dest/p.relative_to(origin);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
dest=r/'exact-engine-source';dest.mkdir()
for current,dirs,names in os.walk(engine/'tool'):
 dirs[:]=[d for d in dirs if d!='target']
 for n in names:
  p=Path(current)/n;out=dest/p.relative_to(engine/'tool');out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
shutil.copyfile(engine/'SEARCH-DECLARATION.json',dest/'ORIGINAL-ENGINE-DECLARATION.json');shutil.copyfile(old/'SOURCE-FREEZE.json',r/'GATED-SOURCE-FREEZE.json');shutil.copyfile(old/'FINISHED-RESULT-v2.json',r/'GATED-NATIVE-RECORD-AUDIT.json');files=[]
for current,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in ['candidate','__pycache__'])
 for n in sorted(names):
  p=Path(current)/n
  if 'resource-preflight'in n or n in ['final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:continue
  files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'review':review},indent=2)+'\n')
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as a:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'final-evidence.tar.gz'),'archive_bytes':(r/'final-evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(json.dumps(review),flush=True)
