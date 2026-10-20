from pathlib import Path
import ast,shutil
a=Path(__file__).parent;r=a.parent/'breakthrough-dense-exact-verifier-20261020';original=(r/'parent-screen.rs').read_text();s=original
start=s.index('let mut prepared=prepared.into_inner().unwrap();prepared.sort_by_key');end=s.index('total_confirm+=t.elapsed().as_secs_f64();',start)
s=s[:start]+'''let prepared=prepared.into_inner().unwrap();let t=std::time::Instant::now();for result in dense_confirm(prepared,&p,&regs,nq as usize,nb as usize,&curve,threads){if result["pass"]==true{best.fetch_min(result["nonce"].as_u64().unwrap(),Ordering::SeqCst);}writeln!(out.lock().unwrap(),"{result}").unwrap();}''' +s[end:]
s+='''
// Repacking changes only exact verifier scheduling. Circuit, FS and full-state classifier are unchanged.
fn dense_step(prefix:&Compact,prepared:Vec<PreparedPacket>,batch:usize,regs:&[Vec<QubitOrBit>],nq:usize,nb:usize,curve:&FastCurveC)->(Vec<PreparedPacket>,Vec<serde_json::Value>){
 let len=prepared.len();assert!(len>0&&len<=8);let contexts=std::array::from_fn(|j|prepared[j.min(len-1)].ctx.0 as *const c_void);let lanes=std::array::from_fn(|j|prepared[j.min(len-1)].lane as u32);let mut ctx=Shake8::combine(contexts,lanes);
 let mixed=ctx.copy().squeeze(64);for j in 0..len{let original=prepared[j].ctx.copy().squeeze(64);assert_eq!(&mixed[j*64..(j+1)*64],&original[prepared[j].lane*64..(prepared[j].lane+1)*64],"Every-round dense SHAKE lane routing mismatch");}
 let metadata:Vec<_>=prepared.iter().map(|p|(p.nonce,p.selected,p.hit,p.prepsecs)).collect();let mut packets:Vec<_>=prepared.into_iter().map(|p|p.packet).collect();while packets.len()<8{packets.push(Packet{keys:Vec::new(),next:NUM_TESTS,batches:Vec::new()});}
 let mut active=[false;8];for j in 0..len{active[j]=packets[j].ensure(batch,curve);}let results=if active.iter().any(|x|*x){let rng=ctx.words(prefix.rng_count);exact_batch(prefix,&packets,[batch;8],active,regs,nq,nb,&rng)}else{["inactive";8]};let shared=Arc::new(ctx);let mut survivors=vec![];let mut rows=vec![];
 for(j,packet)in packets.into_iter().take(len).enumerate(){let(nonce,selected,hit,prepsecs)=metadata[j];if active[j]&&results[j]=="pass"{survivors.push(PreparedPacket{packet,ctx:shared.clone(),lane:j,nonce,selected,hit,prepsecs});}else{let pass=!active[j];rows.push(serde_json::json!({"nonce":nonce,"pass":pass,"kind":if pass{"pass"}else{results[j]},"batches_run":if pass{batch}else{batch+1},"exact_witness_batch":if pass{None}else{Some(batch)},"prepared_batches":packet.batches.len(),"rejection_policy":"exact_full_state_only","verifier_schedule":"dense_survivor_repacking","actual_rng_words_per_executed_batch":prefix.rng_count}));}}
 (survivors,rows)
}
fn dense_confirm(mut alive:Vec<PreparedPacket>,prefix:&Compact,regs:&[Vec<QubitOrBit>],nq:usize,nb:usize,curve:&FastCurveC,threads:usize)->Vec<serde_json::Value>{
 let mut batch=0;let mut rows=vec![];while !alive.is_empty(){assert!(batch<=NUM_TESTS.div_ceil(64));alive.sort_by_key(|x|x.nonce);let mut iter=alive.into_iter();let mut groups=std::collections::VecDeque::new();loop{let group:Vec<_>=iter.by_ref().take(8).collect();if group.is_empty(){break;}groups.push_back(group);}let queue=Mutex::new(groups);let next=Mutex::new(Vec::new());let finished=Mutex::new(Vec::new());std::thread::scope(|scope|{for _ in 0..threads{let queue=&queue;let next=&next;let finished=&finished;scope.spawn(move||loop{let Some(group)=queue.lock().unwrap().pop_front()else{break};let(survivors,done)=dense_step(prefix,group,batch,regs,nq,nb,curve);next.lock().unwrap().extend(survivors);finished.lock().unwrap().extend(done);});}});rows.extend(finished.into_inner().unwrap());alive=next.into_inner().unwrap();batch+=1;}rows
}
'''
(r/'dense-screen.rs').write_text(s)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('tool/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
driver='''import hashlib,json,os,shutil,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-public140-nonce-20261020';t=r/'tool';ops=ws/'breakthrough-public-best-drop-finished-20261020/candidate/ops.bin';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args,name,env=None):
 start=time.time()
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(args,cwd=t,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name;return time.time()-start
try:
 parent=json.loads((old/'SEARCH-DECLARATION.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in parent['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in parent['libraries'].items());assert sha(ops)=='6192778816154b713a714446b3e7d28165a649460173a3e3f17d9de06fa7bb96';assert(r/'parent-screen.rs').read_bytes()==(old/'tool/src/screen.rs').read_bytes()
 t.mkdir();shutil.copytree(old/'tool/src',t/'src');shutil.copyfile(old/'tool/Cargo.toml',t/'Cargo.toml');shutil.copyfile(old/'tool/Cargo.lock',t/'Cargo.lock');shutil.copyfile(r/'dense-screen.rs',t/'src/screen.rs');subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
 sources={p.relative_to(t).as_posix():sha(p)for p in(t/'src').glob('*.rs')};sources.update({n:sha(t/n)for n in['Cargo.toml','Cargo.lock']});freeze={'at_utc':datetime.now(timezone.utc).isoformat(),'tool_source_files':sources,'libraries':parent['libraries'],'parent_engine_freeze_sha256':sha(old/'SEARCH-DECLARATION.json'),'candidate_stream_sha256':sha(ops),'controls':'First1024product nonces, already being screened by unchanged production, repeated by both engines only as controls. Each exact failure kind/firstwitness/batches/pass must match. Additional8partial/24protected fullstate controls; positive complete packet depth12nonce41. No production nonce search, circuit/gate/FS changes or resource score.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\\n');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--locked'],'build');exe=t/'target/release/value_prefilter';(r/'BINARY.sha256').write_text(sha(exe)+'\\n')
 args=[str(exe),str(ops),'1','1024','16',str(r/'dense-controls.jsonl'),'UNUSED','1024'];run(args,'qualification',dict(os.environ,QUALIFY='1'));assert'QUALIFICATION_PASS'in(r/'qualification.log').read_text()
 dense_seconds=run(args,'dense-controls');reference=old/'tool/target/release/value_prefilter';reference_seconds=run([str(reference),str(ops),'1','1024','16',str(r/'reference-controls.jsonl'),'UNUSED','1024'],'reference-controls')
 def rows(name):
  result={}
  for line in(r/name).read_text().splitlines():
   v=json.loads(line);assert v['nonce']not in result;result[v['nonce']]=v
  assert sorted(result)==list(range(1,1025));return result
 dense,ref=rows('dense-controls.jsonl'),rows('reference-controls.jsonl');keys=['pass','kind','batches_run','exact_witness_batch'];assert all(all(dense[k][x]==ref[k][x]for x in keys)for k in dense)
 positive=ws/'breakthrough-depth12-final-20261020/candidate/ops.bin';assert sha(positive)=='63370be6078a4a80454d5174a5f07bfac094fea6af3dd526f77dc8194012cc29';run([str(exe),str(positive),'41','1','1',str(r/'positive-control.jsonl'),'UNUSED','1'],'positive-control');p=json.loads((r/'positive-control.jsonl').read_text());assert p['nonce']==41 and p['pass']and p['batches_run']==141;assert'SELECTED_OFFICIAL_REPLAY nonce=41 ok=true shots=9024 classical=0 phase=0 ancilla=0'in(r/'positive-control.log').read_text()
 assert all(sha(t/p)==h for p,h in sources.items())and all(sha(Path(p))==h for p,h in parent['libraries'].items());result={'status':'EXACT_DENSE_CONTROL_QUALIFICATION_PASS_NOT_PRODUCTION_SEARCH','product_comparison_controls':1024,'additional_control_attempts':2057,'protected_full_state_control_batches':24,'positive_other_source_complete_packet':{'stream_sha256':sha(positive),'nonce':41,'protected9024pass':True},'dense_seconds':dense_seconds,'reference_seconds':reference_seconds,'speedup':reference_seconds/dense_seconds,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'binary_sha256':sha(exe),'dense_rows_sha256':sha(r/'dense-controls.jsonl'),'reference_rows_sha256':sha(r/'reference-controls.jsonl'),'scope':freeze['controls']};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\\n');(r/'run.exit').write_text('0\\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\\n');raise
''';ast.parse(driver);(r/'run.py').write_text(driver)
(r/'PLAN.md').write_text('''# Exact dense verifier qualification and control-only timing

Candidate61927788/gate unchanged; no quantum source or FS modification. Repack
surviving nonce lanes after each full simulator batch; exact backend, original
RNG words and fullstate classifier unchanged. All active states have consumed
identical bytecounts. SHAKE combine validates positions; every regroup compares
64bytes/lane against originalctx clone. Surviving nonce gets exact advanced
ctx+newlane. Failednonce finalstate witness retained; no model/IR rejection.

Freeze engine/libraries before8nonce partial/24protectedfullstate qualification.
Then repeat first1024 already-screened product nonces in both engines solely as
controls,16workers/1024windows; assert exact pass/kind/firstfailure/batchcount
equality. Record every additional2056 productcontrol attempt (8+1024+1024).
One separate positive control: officialdepth12 selectedstream63370be6,nonce41,
all141batches plus protected9024 replay. Total2057partial/controlattempts; not
newproductionselection. No candidate/gate/census change. No Toffoli/Q score.
Only after fullPASS and useful speed may a separate declared continuation be
considered. Existing original search/continuation and finalpipeline unchanged.
''');print(r)
