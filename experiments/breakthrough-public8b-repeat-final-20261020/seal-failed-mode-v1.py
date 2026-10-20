"""Review and preserve exact final source before the user-authorized upload."""
import hashlib,json,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';research=ws/'breakthrough-public8b-repeat-generic-20261020';gate=ws/'breakthrough-public8b-repeat-final-gate-20261020';search=ws/'breakthrough-public8b-repeat-nonce-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
assert(r/'run.exit').read_text().strip()=='0'and not(r/'FINAL-VERIFICATION.json').exists()
f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());g=json.loads((gate/'GATE-RESULT.json').read_text());d=json.loads((gate/'GATE-DECLARATION.json').read_text());sr=json.loads((search/'SEARCH-RESULT.json').read_text())
assert git('rev-parse','HEAD').decode().strip()==f['base']=='58561741282970059dbdd26d3ba8c40cbafd909f';assert len(f['source_files'])==194 and len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert{p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}==set(f['source_files'])
protected=[p for p in git('ls-files').decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
for p in protected:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert(t/'results.tsv').read_bytes()==git('show','HEAD:results.tsv')
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='public8b-repeat-generic-final-20261020-v1';assert g['batches']==32768 and g['candidate_minus_parent_mean_executed_toffoli']==-3.0 and g['paired_standard_error']==0
assert sha(research/'SOURCE-FREEZE-v2.json')==g['candidate_source_freeze_sha256']==f['nonce0_freeze_sha256']=='a680f4d979df3ebdc5601616569705df1f115ebfcc059945d6c2cb3a183c53ab';assert sha(research/'candidate/ops.bin')==g['candidate_stream_sha256']=='4fb7a65acb7027fe9fa519b0db781f830c5cf1e1e5573afa102247401b3b6a01';assert f['gate_result_sha256']==sha(gate/'GATE-RESULT.json')
rows=[json.loads(x)for x in(search/'production.jsonl').read_text().splitlines()];assert sorted(x['nonce']for x in rows)==list(range(1,sr['highest_screened']+1));passes=sorted(x['nonce']for x in rows if x['pass']);k=sr['selected_nonce'];assert passes and min(passes)==k==f['nonce'];assert len(rows)==sr['production_screens']and sha(search/'production.jsonl')==sr['production_rows_sha256'];assert json.loads((search/'QUALIFICATION.json').read_text())['status']=='PASS';assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0'in(search/'search.log').read_text()
assert b['status']=='COMPLETE_UNCHANGED_BENCHMARK_PASS'and b['tested_shots']==9024 and b['qubits']==1464;assert sha(t/'ops.bin')==b['native_receipt']['stream_sha256']and b['native_receipt']['pre_tail_byte_identical_to_gated_source'];assert 'all 9024 shots OK'in(r/'benchmark.log').read_text();assert b['product']==b['qubits']*b['rounded_mean_executed_toffoli']
with tarfile.open(r/'point-add-source.tar.gz')as a:
 assert{m.name for m in a.getmembers()}==set(f['source_files'])
 for p,h in f['source_files'].items():assert hashlib.sha256(a.extractfile(p).read()).hexdigest()==h
assert sha(r/'point-add-source.tar.gz')==f['source_archive_sha256']
for p in sorted(f['source_files']):
 blob=git('hash-object','-w','--no-filters',p).decode().strip();git('update-index','--add','--cacheinfo','100644,'+blob+','+p);assert git('cat-file','blob',':'+p)==(t/p).read_bytes()
changed=git('diff','--cached','--name-only').decode().splitlines();assert changed==['src/point_add/finished_pipeline.rs'];git('commit','-q','-m',f'Repeat generic exact simplification after154 leases at nonce{k}')
revision=git('rev-parse','HEAD').decode().strip();(r/'source.patch').write_bytes(git('diff','--binary',f['base'],'HEAD','--','src/point_add'));assert sha(r/'source.patch')==f['patch_sha256']
for p,h in{**f['source_files'],**f['protected_files']}.items():assert sha(t/p)==h
review={'status':'COMPLETE_LOCAL_REVIEW_PASS_READY_FOR_AUTO_SUBMISSION','at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'base':f['base'],'source_files':194,'protected_files_checked':17,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'benchmark_result_sha256':sha(r/'BENCHMARK-RESULT.json'),'gate_declaration_sha256':sha(gate/'GATE-DECLARATION.json'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'native_receipt':b['native_receipt'],'qubits':b['qubits'],'rounded_mean_executed_toffoli':b['rounded_mean_executed_toffoli'],'product':b['product'],'nonce':k,'production_screens':len(rows),'highest_screened':sr['highest_screened'],'passes':passes,'overrun_first':k+1,'overrun_last':sr['highest_screened'],'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140','selected_protected_packet_passed':True,'unchanged_benchmark_passed_shots':9024,'historical_results_restored':True,'tracked_changes_only_point_add':True,'submission_mode':'auto','user_authorization':'20October2026:submit every new verified improvement for challenge verification','ai_model':'GPT-6 sol','coding_harness':'Codex','scope':'Complete benchmark reproduction. Fresh public minimum must be checked immediately before upload. Component results remain separate; global product record is not beaten.'};save('FINAL-VERIFICATION.json',review)
note=f"""Model: GPT-6 sol
Harness: Codex

# Exact repeated simplification: Q{b['qubits']} / T{b['rounded_mean_executed_toffoli']}

The unchanged challenge benchmark passes all9,024 protected shots, at
**{b['qubits']} logical qubits**, **{b['rounded_mean_executed_toffoli']} rounded
mean executed Toffolis** (mean {b['mean_executed_toffoli']}, total {b['total_executed_toffoli']}).
Product **{b['product']}**. Against the parent's protected packet T751027,
this packet improves {751027-b['rounded_mean_executed_toffoli']} rounded Toffolis.
The independent paired census measures exactly three fewer Toffolis; packet
variation accounts for the additional difference. The nonce was selected only
as the lowest complete pass, never by its Toffoli count.
This targets the independent minimum-Toffoli
objective. The global product incumbent939,138,168 remains lower.

## Source and change

Direct parent is our officially evaluated8b682cf8-e242-4827-bb54-3c0724635893,
Q1464/T751027, public source58561741282970059dbdd26d3ba8c40cbafd909f.
All194 source files and17 protected tracked files were independently compared
as Git objects with the validated local parent1b550a01; every byte matches.
This descendant runs the existing generic exact simplification pipeline once
more after the154 exact product leases, before the fixed96-X identity tail.
The finished pipeline removes three additional unconditional Toffolis. All
arithmetic, precision, public row schedule, original raw stream checks,
source-bound154 lease proof and inherited generic pass implementations remain.
No new arithmetic/table/correctness cut or packet-based content choice.

Source revision {revision}. Only src/point_add/finished_pipeline.rs differs
from the direct source parent. All17 protected files, pinned tools and
historical results remain byte-identical. Source archive SHA256
{review['source_archive_sha256']}; patch SHA256
{review['source_patch_sha256']}. Native27 controls passed before the gate.
All earlier failed gates remain final; no earlier verdict is rejudged.
The compact-fold/core research is separate and is not included in this source.

## Sole predeclared fresh-input gate

Declared at {d['declared_at_utc']}, label
public8b-repeat-generic-final-20261020-v1,32,768 batches of64 shots,
2,097,152 fresh shots per source. Parent is exact official8b stream
77d43b25b1526603b8e496da5f514a1b397a849bdd6eb9511e11beb0536e3057;
frozen candidate nonce0 stream
4fb7a65acb7027fe9fa519b0db781f830c5cf1e1e5573afa102247401b3b6a01.
Declaration SHA256 {review['gate_declaration_sha256']}; result SHA256
{review['gate_result_sha256']}.

|Measurement|Parent|Candidate|
|---|---:|---:|
|Wrong-value shots|1224|1224|
|Phase-failing shots|632|632|
|Dirty-ancilla shots|0|0|
|Failed batches|1260|1260|
|Failed batches per9024-shot packet|5.4217529296875|5.4217529296875|
|Mean executed Toffolis|751025.4625582695|751022.4625582695|

Wrong-value failing shot IDs are identical. Newly failing batches b0 and newly
passing batches c0, one-sided exact McNemar p1.0. Mean difference-3.0,
paired standard error0.0. All four declared criteria pass: no more value
failures, paired p>=0.05,<=18 failed batches per packet, zero dirty shots.
This independent finished circuit was gated once. No rerun, changed label,
extended batch count or changed nonce was used to reverse a failed verdict.

The initial research freeze inherited parent-selected nonce209 and unrelated
final-packaging metadata, while its source hashes already bound nonce0.
An explicitly preserved metadata-only correction retains the original freeze
and result, and binds the current source to nonce0. No source, circuit, test,
build, input or generation was changed or rerun for that correction.

## Nonce and unchanged benchmark

Only after the gate passed, the frozen circuit was screened in ascending order.
**Nonce{k}** is the lowest pass. **{len(rows)} production screens**,1 through
{sr['highest_screened']}, are retained, with all passing nonces{passes} and
parallel overrun{k+1}..{sr['highest_screened']} disclosed. Additional controls
1..8 are partial official packets repeated in production;24 protected full
qubit/classical/phase/RNG states, curve and partial-mask checks at batches
0,70,140 requalify the unchanged exact engine on this circuit.
No arithmetic rejection filter is used. No nonce is chosen by Toffoli count.

The selected nonce independently passes the protected full9024-attempt packet.
Final source changes only the nonce literal from the gated source; every
pre-tail record is byte-identical. Selected native stream SHA256
{b['native_receipt']['stream_sha256']}; canonical records SHA256
{b['native_receipt']['records_sha256']}; pre-tail SHA256
{b['native_receipt']['pre_tail_sha256']}.
The unchanged benchmark then rebuilds this source and passes all9024 shots.

## Reproduction, provenance and limits

Use the challenge's pinned compiler/dependencies and unchanged benchmark.sh.
Frozen source, patch, native/benchmark logs, raw census rows and declarations,
nonce controls/screens, original and corrected metadata, source/stream hashes
and local archive-member verification are preserved in the dated
breakthrough-public8b-repeat-* research packages. The source content comes
from the declared direct parent and inherited public implementations, with
their attribution retained. This reports a measured resource improvement;
no independent novelty or universal correctness claim. Inherited approximate
arithmetic remains, and finite protected-packet success is not all-input
correctness. Research attribution:MonitSharma; AI model:GPT-6 sol; harness:Codex.
"""
for a,z in {
 'all9,024':'all 9,024','all9024':'all 9024','All194':'All 194','and17':'and 17',
 'incumbent939':'incumbent 939','source585':'source 585','parent1b550':'parent 1b550',
 'the154':'the 154','fixed96-X':'fixed 96-X','All17':'All 17','Native27':'Native 27',
 'v1,32,768':'v1, 32,768','of64':'of 64','nonce0':'nonce 0',
 'batches b0 and':'batches b = 0 and','batches c0,':'batches c = 0,','McNemar p1.0':'McNemar p = 1.0','difference-3.0':'difference -3.0',
 'error0.0':'error 0.0','nonce209':'nonce 209',
 'conditions,<=18':'conditions, <=18','p>=0.05,<=18':'p >= 0.05, <=18',
 'per9024':'per 9024','**Nonce':'**Nonce ','screens**,1':'screens**, 1',
 'controls\n1..8':'controls\n1..8',';24':'; 24','batches\n0,70,140':'batches\n0, 70, 140',
 'attribution:MonitSharma':'attribution: MonitSharma','model:GPT':'model: GPT','harness:Codex':'harness: Codex'
}.items():note=note.replace(a,z)
for digest in [review['source_archive_sha256'],review['source_patch_sha256'],review['gate_declaration_sha256'],review['gate_result_sha256'],b['native_receipt']['stream_sha256'],b['native_receipt']['records_sha256'],b['native_receipt']['pre_tail_sha256'],g['candidate_stream_sha256'],g['parent_stream_sha256']]:assert digest in note
(r/'SUBMISSION-NOTE.md').write_text(note)
save('DEPENDENCIES.json',[{'submissionId':'8b682cf8-e242-4827-bb54-3c0724635893','rationale':'Direct source predecessor and exact final-gate parent. Repeat the unchanged generic exact passes after its154 leases; inherited arithmetic and attribution remain.','evidence':f"Public source{f['base']}; final source{revision}; source archive{review['source_archive_sha256']}; patch{review['source_patch_sha256']}."}])
files={}
for p in r.iterdir():
 if p.is_file()and'resource-preflight'not in p.name and p.name not in['EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','final-evidence.tar.gz']:files[p.name]=p
for prefix,directory in [('gate',gate),('search',search),('research',research)]:
 for p in directory.iterdir():
  if p.is_file()and'resource-preflight'not in p.name and p.name not in['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:files[prefix+'/'+p.name]=p
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p)for n,p in files.items()},'scope':'Full final source archive, unchanged benchmark, sole gate rows, exact nonce controls/screens and original metadata/failure evidence. No resource-preflight or credentials.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as a:
 for n,p in sorted(files.items()):a.add(p,arcname=n,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
