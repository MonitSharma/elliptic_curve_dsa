import json,hashlib,os,shutil,socket,subprocess,traceback
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';dev=ws/'breakthrough-borrowed-recycle-development-20261021';gate=ws/'breakthrough-borrowed-recycle-final-gate-20261021';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd):
 with(r/(name+'.log')).open('xb')as out:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,(name,rc)
try:
 assert socket.gethostname()=='LHC-104-070'and (r/'pipeline.exit').read_text().strip()=='0'
 available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2
 (r/'validation-resource-preflight.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'available_kib':available,'cpus':os.cpu_count(),'development_workers':4,'census_workers_total':16,'library_threads':1,'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{x:shutil.which(x)for x in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,comm,pcpu,rss','--sort=-pcpu']).decode()},indent=2)+'\n')
 f=json.loads((r/'SOURCE-FREEZE.json').read_text());v=json.loads((r/'RESULT.json').read_text());assert v['native_tests']==21 and v['qubits']==1464 and sha(r/'SOURCE-FREEZE.json')==v['source_freeze_sha256'];assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());assert sha(t/'ops.bin')==v['stream_sha256'];assert not(gate/'GATE-DECLARATION.json').exists()
 parent=ws/'breakthrough-recycle-final-20261021';pr=json.loads((parent/'PUBLIC-SOURCE-VERIFICATION.json').read_text());assert pr['public_submission']=='cb2253eb-7318-416b-8c9e-af9a28bda867'and pr['public_source_revision']=='90c5d46f8394eb584ab15b6d0bc2969a66f86b17';paths={'official_cb2253':Path(pr['exact_parent_stream']),'borrowed':t/'ops.bin'};assert sha(paths['official_cb2253'])==pr['exact_parent_stream_sha256']
 (dev/'PLAN.json').write_text(json.dumps({'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'cb2253-borrowed13-development-20261021-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'scope':'First fresh development for fixed13originaldonor source207/native21/official-local bytes. Current officialcb2253 comparator, all target/other hashes and failure identities. No score or gate verdict from development.'},indent=2)+'\n')
 run(['python3',str(dev/'diagnostic.py')],'current-parent-development',dev);(dev/'controller.exit').write_text('0\n');run(['python3',str(gate/'run.py')],'sole-final-gate',gate)
 g=json.loads((gate/'GATE-RESULT.json').read_text());(r/'VALIDATION-RESULT.json').write_text(json.dumps({'status':'OWN_FINAL_GATE_PASS_AWAIT_SOURCE_QUALIFIED_NONCE'if g['verdict']=='FAILURE_RATE_GATE_PASS'else'OWN_FINAL_GATE_FAIL_RETIRED','gate_verdict':g['verdict'],'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'scope':'OutcomeFINAL. No nonce/benchmark/upload by this controller; only separately qualified postPASS source engine and unchangedbenchmark may proceed.'},indent=2)+'\n');(r/'validation.exit').write_text('0\n')
except BaseException:
 (r/'validation.exit').write_text('1\n');(r/'VALIDATION-ERROR.txt').write_text(traceback.format_exc());raise
