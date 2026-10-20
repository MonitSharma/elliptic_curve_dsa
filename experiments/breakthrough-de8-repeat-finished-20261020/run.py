import hashlib,json,os,re,shutil,socket,subprocess,tarfile,time,traceback
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as out:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,(name,rc)
try:
 assert socket.gethostname()=='LHC-104-070';available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2
 save(r/'resource-preflight.json',{'at':datetime.now(timezone.utc).isoformat(),'hostname':socket.gethostname(),'available_kib':available,'cpus':os.cpu_count(),'uptime':subprocess.check_output(['uptime']).decode(),'scheduler':{s:shutil.which(s)for s in ['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,pcpu,pmem,args','--sort=-pcpu']).decode(),'build_threads':4,'max_census_threads':16,'max_nonce_threads':8})
 spec=json.loads((r/'SOURCE-SPEC.json').read_text());assert not t.exists();run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),spec['base']],'worktree',r)
 assert len(spec['protected_files'])==17 and all(sha(t/p)==h for p,h in spec['protected_files'].items())
 with tarfile.open(r/'point-add-source.tar.gz')as ar:
  members=ar.getmembers();assert {m.name for m in members}==set(spec['source_files'])
  for m in members:
   path=Path(m.name);assert m.isfile()and not path.is_absolute()and'..'not in path.parts and m.name.startswith('src/point_add/');data=ar.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==spec['source_files'][m.name];p=t/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 assert all(sha(t/p)==h for p,h in {**spec['source_files'],**spec['protected_files']}.items());run(['git','add','--','src/point_add'],'stage');run(['git','commit','-m','Freeze exact two cache holds and repeated generic simplification at nonce zero'],'source-commit');revision=subprocess.check_output(['git','-C',str(t),'rev-parse','HEAD']).decode().strip()
 (r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary',spec['base'],'HEAD','--','src/point_add']))
 freeze=dict(spec,source_revision=revision,source_spec_sha256=sha(r/'SOURCE-SPEC.json'),source_archive_sha256=sha(r/'point-add-source.tar.gz'),source_patch_sha256=sha(r/'source.patch'));save(r/'SOURCE-FREEZE.json',freeze)
 run(['cp','-a','--reflink=auto',str(ws/'breakthrough-exact-witness-final-20261020/candidate/target'),str(t/'target')],'reuse-build',r)
 env=dict(os.environ,CARGO_BUILD_JOBS='4',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PEBBLE_HARD_CAP='1234');cargo='/home/hclau/.cargo/bin/cargo'
 for filt,n in [('witness_context_cache::cache_tests',1),('repeat_generic_cache::cache_tests',1),('exact_witness_ripple_tests',4),('exact_shared_sum_tests',1),('grouped_plan_shape_tests',1)]:
  name='native-'+filt.replace('::','-');run([cargo,'+1.93.0','test','--release','--locked','--bin','build_circuit',filt,'--','--nocapture','--test-threads=1'],name,env=env);assert f'test result: ok. {n} passed; 0 failed;'in(r/(name+'.log')).read_text()
 run([cargo,'+1.93.0','build','--release','--locked','--bin','build_circuit'],'build',env=env);run(['timeout','1800',str(t/'target/release/build_circuit')],'generate',env=env)
 assert all(sha(t/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items());assert sha(t/'ops.bin')==spec['expected_stream_sha256']
 stats=ws/'breakthrough-stackv3-width-stats-20261020/tool/target/release/native_width_stats';run([str(stats),str(t/'ops.bin'),str(r/'OUTPUT-STATS.json')],'stats',r);st=json.loads((r/'OUTPUT-STATS.json').read_text());assert st['records_sha3']==spec['expected_records_sha3']and st['operations']==spec['operations']and st['qubits_protected_analyzer']==1464
 save(r/'RESULT.json',{'status':'FIXED_EXACT_REPEAT_FINISHED_NONCE0_NOT_GATED_OR_SCORED','native_tests':8,'independent_proof_controls':9,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'stream_sha256':sha(t/'ops.bin'),'operations':st['operations'],'qubits':1464,'records_sha3':st['records_sha3'],'scope':freeze['scope']});(r/'run.exit').write_text('0\n')
 dev=ws/'breakthrough-de8-repeat-finished-development-20261020';parent=ws/'breakthrough-exact-witness-final-20261020/candidate/ops.bin';assert sha(parent)=='131712cc9c79e9ffd3ac60c07d097a29b5252c03afa95c891c5ecdd603c60c2e';paths={'official_de8':parent,'generic':t/'ops.bin'}
 save(dev/'PLAN.json',{'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'de8-repeat-finished-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'scope':'Fresh512x64/full-output finished-source development, native8/proof9/complete source/stream bindings passed. No gate/nonce/benchmark/score.'})
 run(['python3',str(dev/'diagnostic.py')],'finished-development',dev,env);(dev/'controller.exit').write_text('0\n')
 gate=ws/'breakthrough-de8-repeat-final-gate-20261020';run(['python3',str(gate/'run.py')],'sole-final-gate',gate,env);g=json.loads((gate/'GATE-RESULT.json').read_text())
 if g['verdict']!='FAILURE_RATE_GATE_PASS':save(r/'PIPELINE-RESULT.json',{'status':'FINAL_GATE_FAIL_NO_NONCE','gate':g['verdict']})
 else:
  nonce=ws/'breakthrough-de8-repeat-nonce-20261020';run(['python3',str(nonce/'run.py')],'qualified-nonce',nonce,env);sr=json.loads((nonce/'SEARCH-RESULT.json').read_text())
  if sr['status']!='LOWEST_PASS_FOUND':save(r/'PIPELINE-RESULT.json',{'status':'FINITE_NONCE_PREFIX_EXHAUSTED','search':sr})
  else:
   final=ws/'breakthrough-de8-repeat-final-20261020';run(['python3',str(final/'finalize.py')],'unchanged-benchmark',final,env);save(r/'PIPELINE-RESULT.json',{'status':'COMPLETE_LOCAL_BENCHMARK_READY_FOR_LOCAL_EVIDENCE_REVIEW','benchmark_result_sha256':sha(final/'BENCHMARK-RESULT.json'),'scope':'No upload yet. Independently verify all source/evidence locally, refresh public currenttarget and automatically submit only if it improves currentrecord.'})
 (r/'pipeline.exit').write_text('0\n')
except BaseException:
 if not(r/'run.exit').exists():(r/'run.exit').write_text('1\n')
 (r/'pipeline.exit').write_text('1\n');(r/'PIPELINE-ERROR.txt').write_text(traceback.format_exc());raise
