import hashlib,json,os,shutil,socket,subprocess,tarfile,traceback,time
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as out:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,(name,rc)
try:
 assert socket.gethostname()=='LHC-104-070';available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2
 save(r/'resource-preflight.json',{'at_utc':datetime.now(timezone.utc).isoformat(),'hostname':socket.gethostname(),'available_kib':available,'cpus':os.cpu_count(),'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{s:shutil.which(s)for s in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,comm,pcpu,rss','--sort=-pcpu']).decode(),'build_threads':4,'library_threads':1,'census_threads_total':16})
 spec=json.loads((r/'SOURCE-SPEC.json').read_text());assert sha(r/'point-add-source.tar.gz')==spec['source_archive_sha256']and sha(r/'source.patch')==spec['source_patch_sha256'];assert not t.exists()
 run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),spec['base']],'worktree',r);assert len(spec['protected_files'])==17 and all(sha(t/p)==h for p,h in spec['protected_files'].items())
 with tarfile.open(r/'point-add-source.tar.gz')as ar:
  assert {m.name for m in ar.getmembers()}==set(spec['source_files'])
  for m in ar.getmembers():
   path=Path(m.name);assert m.isfile()and not path.is_absolute()and'..'not in path.parts and m.name.startswith('src/point_add/');data=ar.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==spec['source_files'][m.name];p=t/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 assert all(sha(t/p)==h for p,h in{**spec['source_files'],**spec['protected_files']}.items());run(['git','add','--','src/point_add'],'stage');run(['git','commit','-m','Freeze exact original-measurement recycling at nonce zero'],'source-commit');revision=subprocess.check_output(['git','-C',str(t),'rev-parse','HEAD']).decode().strip();(r/'git-source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary',spec['base'],'HEAD','--','src/point_add']));freeze=dict(spec,source_revision=revision,source_spec_sha256=sha(r/'SOURCE-SPEC.json'),git_source_patch_sha256=sha(r/'git-source.patch'));save(r/'SOURCE-FREEZE.json',freeze)
 assert shutil.disk_usage(ws).free>15*1024**3;run(['cp','-a','--reflink=auto',str(ws/'breakthrough-de8-repeat-final-20261020/candidate/target'),str(t/'target')],'reuse-build',r)
 env=dict(os.environ,CARGO_BUILD_JOBS='4',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PEBBLE_HARD_CAP='1467');cargo='/home/hclau/.cargo/bin/cargo'
 run([cargo,'+1.93.0','test','--release','--locked','--bin','build_circuit','point_add::recycle_measurements::','--','--nocapture','--test-threads=1'],'native',env=env);assert 'test result: ok. 14 passed; 0 failed;'in(r/'native.log').read_text();run([cargo,'+1.93.0','build','--release','--locked','--bin','build_circuit'],'build',env=env);run(['timeout','1800',str(t/'target/release/build_circuit')],'generate',env=env)
 deadline=time.monotonic()+10800
 while not(r/'LOCAL-GENERATION.json').exists():assert time.monotonic()<deadline;time.sleep(2)
 local=json.loads((r/'LOCAL-GENERATION.json').read_text());assert sha(r/'SOURCE-SPEC.json')==local['source_spec_sha256'] and local['native_controls']==14
 assert all(sha(t/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items());assert sha(t/'ops.bin')==local['stream_sha256'],'Crosscompiler must reproduce exact local frozen stream'
 stats=ws/'breakthrough-stackv3-width-stats-20261020/tool/target/release/native_width_stats';run([str(stats),str(t/'ops.bin'),str(r/'OUTPUT-STATS.json')],'stats',r);st=json.loads((r/'OUTPUT-STATS.json').read_text());assert st['qubits_protected_analyzer']==1467 and st['operations']==11292532 and st['records_sha3']==local['records_sha3']
 save(r/'RESULT.json',{'status':'FINISHED_EXACT_RECYCLE_NONCE0_CROSSCOMPILER_NATIVE14_COMPLETE_NOT_GATED_OR_SCORED','native_tests':14,'prior_independent_semantic_proof_controls':11,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'stream_sha256':sha(t/'ops.bin'),'operations':st['operations'],'qubits':1467,'records_sha3':st['records_sha3'],'scope':freeze['scope']});(r/'run.exit').write_text('0\n')
 dev=ws/'breakthrough-recycle-finished-development-20261021';parent=ws/'breakthrough-de8-repeat-final-20261020/candidate/ops.bin';assert sha(parent)==spec['parent_stream_sha256'];paths={'official_ffe20':parent,'recycle':t/'ops.bin'}
 save(dev/'PLAN.json',{'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'ffe20-recycle-finished-development-20261021-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'scope':'Fresh finished-source development only, after native4/independentproof12/local-versus-official1.93 exactstream agreement. Exact public1829 comparator, every target/otherregisterhash and phase/value/dirty outcome retained. No gate/nonce/benchmark/score.'});run(['python3',str(dev/'diagnostic.py')],'finished-development',dev,env);(dev/'controller.exit').write_text('0\n')
 gate=ws/'breakthrough-recycle-final-gate-20261021';run(['python3',str(gate/'run.py')],'sole-final-gate',gate,env);g=json.loads((gate/'GATE-RESULT.json').read_text());save(r/'PIPELINE-RESULT.json',{'status':'FINAL_GATE_PASS_AWAIT_SOURCE_BOUND_ORIGINAL_FS_ENGINE'if g['verdict']=='FAILURE_RATE_GATE_PASS'else'FINAL_GATE_FAIL_RETIRED_NO_NONCE','gate_verdict':g['verdict'],'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'scope':'Outcome final. This controller never starts nonce screening, benchmark or upload. Only PASS permits separately qualified frozen-source ORIGINAL_FS engine, ascending lowestpassingnonce, unchangedbenchmark and authorized automatic official submission.'});(r/'pipeline.exit').write_text('0\n')
except BaseException:
 if not(r/'run.exit').exists():(r/'run.exit').write_text('1\n')
 (r/'pipeline.exit').write_text('1\n');(r/'PIPELINE-ERROR.txt').write_text(traceback.format_exc());raise
