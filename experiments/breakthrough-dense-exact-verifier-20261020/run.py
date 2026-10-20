import hashlib,json,os,shutil,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-public140-nonce-20261020';t=r/'tool';ops=ws/'breakthrough-public-best-drop-finished-20261020/candidate/ops.bin';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args,name,env=None):
 start=time.time()
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(args,cwd=t,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name;return time.time()-start
try:
 parent=json.loads((old/'SEARCH-DECLARATION.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in parent['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in parent['libraries'].items());assert sha(ops)=='6192778816154b713a714446b3e7d28165a649460173a3e3f17d9de06fa7bb96';assert(r/'parent-screen.rs').read_bytes()==(old/'tool/src/screen.rs').read_bytes()
 t.mkdir();shutil.copytree(old/'tool/src',t/'src');shutil.copyfile(old/'tool/Cargo.toml',t/'Cargo.toml');shutil.copyfile(old/'tool/Cargo.lock',t/'Cargo.lock');shutil.copyfile(r/'dense-screen.rs',t/'src/screen.rs');subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
 sources={p.relative_to(t).as_posix():sha(p)for p in(t/'src').glob('*.rs')};sources.update({n:sha(t/n)for n in['Cargo.toml','Cargo.lock']});freeze={'at_utc':datetime.now(timezone.utc).isoformat(),'tool_source_files':sources,'libraries':parent['libraries'],'parent_engine_freeze_sha256':sha(old/'SEARCH-DECLARATION.json'),'candidate_stream_sha256':sha(ops),'controls':'First1024product nonces, already being screened by unchanged production, repeated by both engines only as controls. Each exact failure kind/firstwitness/batches/pass must match. Additional8partial/24protected fullstate controls; positive complete packet depth12nonce41. No production nonce search, circuit/gate/FS changes or resource score.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--locked'],'build');exe=t/'target/release/value_prefilter';(r/'BINARY.sha256').write_text(sha(exe)+'\n')
 args=[str(exe),str(ops),'1','1024','16',str(r/'dense-controls.jsonl'),'UNUSED','1024'];run(args,'qualification',dict(os.environ,QUALIFY='1'));assert'QUALIFICATION_PASS'in(r/'qualification.log').read_text()
 dense_seconds=run(args,'dense-controls');reference=old/'tool/target/release/value_prefilter';reference_seconds=run([str(reference),str(ops),'1','1024','16',str(r/'reference-controls.jsonl'),'UNUSED','1024'],'reference-controls')
 def rows(name):
  result={}
  for line in(r/name).read_text().splitlines():
   v=json.loads(line);assert v['nonce']not in result;result[v['nonce']]=v
  assert sorted(result)==list(range(1,1025));return result
 dense,ref=rows('dense-controls.jsonl'),rows('reference-controls.jsonl');keys=['pass','kind','batches_run','exact_witness_batch'];assert all(all(dense[k][x]==ref[k][x]for x in keys)for k in dense)
 positive=ws/'breakthrough-depth12-final-20261020/candidate/ops.bin';assert sha(positive)=='63370be6078a4a80454d5174a5f07bfac094fea6af3dd526f77dc8194012cc29';run([str(exe),str(positive),'41','1','1',str(r/'positive-control.jsonl'),'UNUSED','1'],'positive-control');p=json.loads((r/'positive-control.jsonl').read_text());assert p['nonce']==41 and p['pass']and p['batches_run']==141;assert'SELECTED_OFFICIAL_REPLAY nonce=41 ok=true shots=9024 classical=0 phase=0 ancilla=0'in(r/'positive-control.log').read_text()
 assert all(sha(t/p)==h for p,h in sources.items())and all(sha(Path(p))==h for p,h in parent['libraries'].items());result={'status':'EXACT_DENSE_CONTROL_QUALIFICATION_PASS_NOT_PRODUCTION_SEARCH','product_comparison_controls':1024,'additional_control_attempts':2057,'protected_full_state_control_batches':24,'positive_other_source_complete_packet':{'stream_sha256':sha(positive),'nonce':41,'protected9024pass':True},'dense_seconds':dense_seconds,'reference_seconds':reference_seconds,'speedup':reference_seconds/dense_seconds,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'binary_sha256':sha(exe),'dense_rows_sha256':sha(r/'dense-controls.jsonl'),'reference_rows_sha256':sha(r/'reference-controls.jsonl'),'scope':freeze['controls']};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');raise
