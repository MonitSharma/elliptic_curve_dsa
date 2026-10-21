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
 assert socket.gethostname()=='LHC-104-070'
 available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2
 save(r/'resource-preflight.json',{'at_utc':datetime.now(timezone.utc).isoformat(),'hostname':socket.gethostname(),'available_kib':available,'cpus':os.cpu_count(),'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{s:shutil.which(s)for s in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,comm,pcpu,rss','--sort=-pcpu']).decode(),'build_threads':4,'library_threads':1})
 spec=json.loads((r/'SOURCE-SPEC.json').read_text());assert sha(r/'point-add-source.tar.gz')==spec['source_archive_sha256'];assert not t.exists()
 save(r/'base-preflight.json',{'hostname':socket.gethostname(),'branch':subprocess.check_output(['git','-C',str(ws/'toffoli'),'branch','--show-current']).decode().strip(),'revision':subprocess.check_output(['git','-C',str(ws/'toffoli'),'rev-parse','HEAD']).decode().strip(),'status':subprocess.check_output(['git','-C',str(ws/'toffoli'),'status','--porcelain']).decode()})
 run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),spec['base']],'worktree',r)
 assert len(spec['protected_files'])==17 and all(sha(t/p)==h for p,h in spec['protected_files'].items())
 with tarfile.open(r/'point-add-source.tar.gz')as ar:
  assert{m.name for m in ar.getmembers()}==set(spec['source_files'])
  for m in ar.getmembers():
   p=Path(m.name);assert m.isfile()and not p.is_absolute()and'..'not in p.parts and m.name.startswith('src/point_add/');data=ar.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==spec['source_files'][m.name];dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 assert all(sha(t/p)==h for p,h in{**spec['source_files'],**spec['protected_files']}.items())
 run(['git','add','--','src/point_add'],'stage');run(['git','commit','-m','Freeze unchanged exact public compact carry constructor grid'],'source-commit')
 revision=subprocess.check_output(['git','-C',str(t),'rev-parse','HEAD']).decode().strip();(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary',spec['base'],'HEAD','--','src/point_add']));save(r/'SOURCE-FREEZE.json',dict(spec,source_revision=revision,source_patch_sha256=sha(r/'source.patch')))
 assert shutil.disk_usage(ws).free>15*1024**3;run(['cp','-a','--reflink=auto',str(ws/'breakthrough-de8-repeat-final-20261020/candidate/target'),str(t/'target')],'reuse-build',r)
 env=dict(os.environ,CARGO_BUILD_JOBS='4',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');cargo='/home/hclau/.cargo/bin/cargo'
 for name,selector,count in [('comparator-tests','compact_compare_tests',4),('plan-tests','stack_plan7_',4),('drop-policy-tests','public_reverse_drop_policy_tests',1)]:
  run([cargo,'+1.93.0','test','--release','--locked','--bin','build_circuit',selector,'--','--nocapture','--test-threads=1'],name,env=env);assert f'test result: ok. {count} passed; 0 failed;'in(r/(name+'.log')).read_text()
 run([cargo,'+1.93.0','build','--release','--locked','--bin','build_circuit'],'build',env=env)
 rows=[];stats=ws/'breakthrough-stackv3-width-stats-20261020/tool/target/release/native_width_stats'
 for mode in spec['modes']:
  assert all(sha(t/p)==h for p,h in{**spec['source_files'],**spec['protected_files']}.items());dest=r/mode;dest.mkdir();start=time.monotonic()
  try:
   run(['timeout','1800',str(t/'target/release/build_circuit')],'generate-'+mode,dest,dict(env,STACK_WIDTH_RESEARCH=mode));path=dest/'ops.bin';row={'mode':mode,'exit':0,'stream_sha256':sha(path),'seconds':time.monotonic()-start}
   if mode=='public':assert row['stream_sha256']==spec['public_exact_sha256'],'Public byte control failed'
   run([str(stats),str(path),str(r/(mode+'-STATS.json'))],'stats-'+mode,r);st=json.loads((r/(mode+'-STATS.json')).read_text());row.update(qubits=st['qubits_protected_analyzer'],operations=st['operations'],diagnostic_weight=st['fair_guard_depth_proxy'],records_sha3=st['records_sha3'])
  except AssertionError:
   if mode=='public':raise
   row={'mode':mode,'exit':int((r/('generate-'+mode+'.exit')).read_text())if(r/('generate-'+mode+'.exit')).exists()else None,'seconds':time.monotonic()-start,'failure':traceback.format_exc()}
  rows.append(row);save(r/'PROGRESS.json',rows);print(json.dumps(row),flush=True)
 assert all(sha(t/p)==h for p,h in{**spec['source_files'],**spec['protected_files']}.items());save(r/'RESULT.json',{'status':'EXACT_CARRY_LAYOUT_GRID_COMPLETE_DIAGNOSTIC_ONLY','cases':rows,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'scope':spec['scope']});(r/'pipeline.exit').write_text('0\n')
except BaseException:
 (r/'pipeline.exit').write_text('1\n');(r/'PIPELINE-ERROR.txt').write_text(traceback.format_exc());raise
