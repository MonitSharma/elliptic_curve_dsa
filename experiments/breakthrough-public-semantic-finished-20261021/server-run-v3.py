import hashlib,json,os,shutil,socket,subprocess,tarfile,traceback
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def run(cmd,name,cwd=t,env=None):
 with(r/('v3-'+name+'.log')).open('xb')as out:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/('v3-'+name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/('v3-'+name+'.exit')).write_text(str(rc)+'\n');assert rc==0,(name,rc)
try:
 assert socket.gethostname()=='LHC-104-070';available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2
 save(r/'resource-preflight-v3.json',{'at_utc':datetime.now(timezone.utc).isoformat(),'hostname':socket.gethostname(),'available_kib':available,'cpus':os.cpu_count(),'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{s:shutil.which(s)for s in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,comm,pcpu,rss','--sort=-pcpu']).decode(),'build_threads':4,'library_threads':1,'census_threads_total':16})
 spec=json.loads((r/'SOURCE-SPEC.json').read_text());freeze=json.loads((r/'SOURCE-FREEZE.json').read_text());result=json.loads((r/'RESULT.json').read_text())
 assert (r/'validation-v2.exit').read_text().strip()=='0'
 assert subprocess.check_output(['git','-C',str(t),'rev-parse','HEAD']).decode().strip()==freeze['source_revision']
 assert all(sha(t/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
 assert sha(r/'SOURCE-FREEZE.json')==result['source_freeze_sha256'] and sha(t/'ops.bin')==result['stream_sha256']
 assert not (ws/'breakthrough-public-semantic-final-gate-20261021/GATE-DECLARATION.json').exists()
 assert not (ws/'breakthrough-public-semantic-finished-development-20261021/public1829.out').exists()
 env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
 dev=ws/'breakthrough-public-semantic-finished-development-20261021';parent=ws/'breakthrough-public1829-reproduction-20261020/parent/ops.bin';assert sha(parent)==spec['parent_stream_sha256'];paths={'public1829':parent,'semantic':t/'ops.bin'}
 save(dev/'PLAN.json',{'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'public1829-semantic-finished-development-20261021-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'scope':'Fresh finished-source development only, after native4/independentproof12/local-versus-official1.93 exactstream agreement. Exact public1829 comparator, every target/otherregisterhash and phase/value/dirty outcome retained. No gate/nonce/benchmark/score.'});run(['python3',str(dev/'diagnostic.py')],'finished-development',dev,env);(dev/'controller.exit').write_text('0\n')
 gate=ws/'breakthrough-public-semantic-final-gate-20261021';run(['python3',str(gate/'run-v3.py')],'sole-final-gate',gate,env);g=json.loads((gate/'GATE-RESULT.json').read_text());save(r/'PIPELINE-RESULT-V3.json',{'status':'FINAL_GATE_PASS_AWAIT_SOURCE_BOUND_ORIGINAL_FS_ENGINE'if g['verdict']=='FAILURE_RATE_GATE_PASS'else'FINAL_GATE_FAIL_RETIRED_NO_NONCE','gate_verdict':g['verdict'],'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'scope':'Outcome final. This controller never starts nonce screening, benchmark or upload. Only PASS permits separately qualified frozen-source ORIGINAL_FS engine, ascending lowestpassingnonce, unchangedbenchmark and authorized automatic official submission.'});(r/'pipeline-v3.exit').write_text('0\n')
except BaseException:
 (r/'pipeline-v3.exit').write_text('1\n');(r/'PIPELINE-ERROR-V3.txt').write_text(traceback.format_exc());raise
