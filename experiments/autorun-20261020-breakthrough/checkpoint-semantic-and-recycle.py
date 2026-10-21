from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,tarfile
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=a.parent
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(root),*args])
previously_staged=set(git('diff','--cached','--name-only').decode().splitlines())
names=['breakthrough-public-semantic-diff-20261021','breakthrough-public-semantic-finished-20261021','breakthrough-public-semantic-finished-development-20261021','breakthrough-public-semantic-final-gate-20261021','breakthrough-semantic-source-value-proof-20261021','breakthrough-global-product-inventory-20261021','breakthrough-recycle-zero-measurements-20261021','breakthrough-recycle-zero-measurements-v2-20261021','breakthrough-recycle-zero-measurements-v3-20261021']
paths=[]
for name in names:
 r=ex/name;fpath=r/'SOURCE-FREEZE.json'
 if fpath.exists() and (r/'local-tool').exists():
  f=json.loads(fpath.read_bytes());files=f.get('tool_source_files',f.get('source_files',{}))
  if files and all((r/'local-tool'/n).is_file() for n in files):
   assert all(sha(r/'local-tool'/n)==h for n,h in files.items())
   with tarfile.open(r/'preserved-tool-source.tar.gz','w:gz')as ar:
    for n in sorted(files):ar.add(r/'local-tool'/n,arcname=n,recursive=False)
   with tarfile.open(r/'preserved-tool-source.tar.gz')as ar:
    assert all(hashlib.sha256(ar.extractfile(m).read()).hexdigest()==files[m.name]for m in ar.getmembers())
 for p in r.rglob('*'):
  rel=p.relative_to(r)
  if any(x in rel.parts for x in ['candidate','local-tool','target','__pycache__']):continue
  if p.name.endswith('.ops.bin') or p.name in ['ops.bin','normalized-value-ir.bin.zst']:continue
  if p.is_file():
   assert p.stat().st_size<20_000_000,(p,p.stat().st_size)
   paths.append(p.relative_to(root).as_posix())
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),active_jobs=[{'where':'smu_server','pid':3272061,'driver':'breakthrough-public-semantic-finished-20261021/server-run-v2.py','scope':'Unchanged source, attempt1 missing build cache preserved, resumed official1.93 validation then fresh development and sole first gate. No nonce before final PASS.'},{'where':'local WSL','windows_pid':29336,'experiment':'breakthrough-recycle-zero-measurements-v3-20261021','scope':'Exact recycled original zero-effect measurement component; native11 and fresh24 fullstate comparisons each parent. V1compile/V2adapter failures preserved.'}],latest_public_snapshot='experiments/breakthrough-assessment-20261020/snapshots/20261021T012631Z',finished_semantic_candidate={'source_revision':'ebd90875a9f5e9a9d5092144fc587e764ec23cb5','source_files':187,'protected_files':17,'stream_sha256':'6523404466e07d3ea6cd94c2246a7ff73954b8aa24a6f4548da210fd84d08f6f','local_native':4,'independent_native':12,'original_server_setup_exit':1,'original_setup_failure':'Missing public-parent build cache; no gate declared, no development executed. Resume preserves original source and failures.','gate_result':'NOT_YET_KNOWN','nonce_screens':0},source_bound_value_proof={'status':'COMPLETE_VERIFICATION_ONLY','native_tool':29,'protected_comparisons':27,'new_stream':'6523404466e07d3ea6cd94c2246a7ff73954b8aa24a6f4548da210fd84d08f6f','value_nodes':7000856,'remaining_random_definitions':309,'fixed_predeclared_old_input_constant_wrong_bits':234,'new_nonce_screens':0,'scope':'Own normalized cache, unchanged qualified binary. No acceptance/phase/dirty shortcut or candidate nonce rejection.'},exact_global_product_inventory={'native':5,'public_product_pair_groups':59,'current_T_pair_groups':13,'triple_groups_both':0,'scope':'Read-only inventory, no circuit/score. IDs local to each symbolic graph; planner rederives all proofs.'},next_product_front='Complete frozen single-CCXtoCX first sole final gate. Exact no-new-RNG zero-effect measurement recycling is independent new source-proved structural front; native11, fullprotected pending. Preserve all final verdicts, no nonce before candidate own gate PASS. Automatically officialsubmit each complete verified improvement as GPT-6 sol/Codex. Newer root commits remain local; exact approved41f769ec push already fulfilled.')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
with(a/'LOG.md').open('a',encoding='utf-8')as out:out.write('\n## '+state['at_utc']+'\nFinished exact public semantic source187/protected17, local native4 and stream652340, official1.93 native4/build PASS. Server setup1 failed missing parent build cache before any gate; preserved failure, unchanged-source continuation PID3272061. Candidate own value proof native29/fresh27 PASS, fixed old input234 constant wrong bits; no nonce. Read-only global product inventory native5:59/13 pairs, zero triples. New source-proved original zero-effect measurement recycling native11 PASS; V1compile/V2adapter failures preserved, V3 whole protected comparisons pending. Global product ACTIVE, auto-submit policy unchanged; newer commits local.\n')
helpers=['PUBLIC-SEMANTIC-PIPELINE-TRANSFER.json','declare-public-semantic-final-gate.py','global-product-inventory.rs','install-public-semantic-server.py','launch-public-semantic-server.py','package-public-semantic-server.py','prepare-global-product-inventory.py','prepare-public-semantic-diff.py','prepare-public-semantic-finished.py','prepare-public-semantic-server-pipeline.py','prepare-semantic-source-value-proof.py','run-public-semantic-server.py','resume-public-semantic-server-v2.py','recycle-zero-measurements.rs','prepare-recycle-zero-measurements.py','checkpoint-semantic-and-recycle.py','CURRENT-ACTIVE.json','LOG.md']
paths += [(a/n).relative_to(root).as_posix() for n in helpers]
paths += ['experiments/breakthrough-assessment-20261020/LATEST.json']
paths += [p.relative_to(root).as_posix() for p in (ex/'breakthrough-assessment-20261020/snapshots/20261021T012631Z').rglob('*') if p.is_file()]
assert previously_staged<=set(paths),'Preserve unrelated staged edits'
subprocess.run(['git','-C',str(root),'add','-f','--',*paths],check=True)
assert set(git('diff','--cached','--name-only').decode().splitlines())<=set(paths)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Freeze exact semantic candidate and qualify zero-measurement recycling controls'],check=True)
print(git('rev-parse','HEAD').decode().strip())
