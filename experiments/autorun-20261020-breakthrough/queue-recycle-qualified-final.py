from pathlib import Path
import subprocess,json
a=Path(__file__).resolve().parent;ex=a.parent
# An earlier attempt to queue this before PASS was rejected by automatic review.
# Require the completed local gate evidence before even preparing remote jobs.
g=json.loads((ex/'breakthrough-recycle-final-gate-20261021/GATE-RESULT.json').read_text())
assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())
assert g['label']=='ffe20-exact-measurement-recycle-final-20261021-v1'
assert g['batches']==32768 and g['shots_per_source']==2097152
n=ex/'breakthrough-recycle-nonce-20261021';r=ex/'breakthrough-recycle-final-20261021';n.mkdir(exist_ok=False);r.mkdir(exist_ok=False)
mapping={'breakthrough-de8-repeat-nonce-20261020':n.name,'breakthrough-de8-repeat-finished-20261020':'breakthrough-recycle-finished-v2-20261021','breakthrough-de8-repeat-final-gate-20261020':'breakthrough-recycle-final-gate-20261021','breakthrough-de8-repeat-final-20261020':r.name,'cache-repeat-generic-final-20261020-v1':'ffe20-exact-measurement-recycle-final-20261021-v1','repeat_generic_cache.rs':'recycle_measurements.rs'}
def adapt(s):
 for x,y in mapping.items():s=s.replace(x,y)
 return s
(n/'run.py').write_text(adapt((ex/'breakthrough-de8-repeat-nonce-20261020/run.py').read_text()))
s=adapt((ex/'breakthrough-de8-repeat-final-20261020/finalize.py').read_text()).replace('import ctypes,ctypes.util,hashlib,json,os,re,shutil,struct,subprocess,tarfile,time','import ctypes,ctypes.util,hashlib,json,os,re,shutil,struct,subprocess,tarfile,time,socket')
marker=' assert not t.exists();run('
insert=""" assert socket.gethostname()=='LHC-104-070';available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2
 save('resource-preflight.json',{'available_kib':available,'cpus':os.cpu_count(),'build_threads':4,'library_threads':1,'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{x:shutil.which(x)for x in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,comm,pcpu,rss','--sort=-pcpu']).decode()})
"""
assert marker in s;s=s.replace(marker,insert+marker,1);(r/'finalize.py').write_text(s)
driver='''import json,os,subprocess,traceback
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-recycle-final-20261021';n=ws/'breakthrough-recycle-nonce-20261021'
env=dict(os.environ,CARGO_BUILD_JOBS='4',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
try:
 with(n/'controller.log').open('xb')as out:
  p=subprocess.Popen(['python3','-u',str(n/'run.py')],stdout=out,stderr=subprocess.STDOUT,env=env);(n/'controller.pid').write_text(str(p.pid)+'\\n');assert p.wait()==0
 sr=json.loads((n/'SEARCH-RESULT.json').read_text())
 if sr['status']=='LOWEST_PASS_FOUND':
  with(r/'finalize.log').open('xb')as out:
   p=subprocess.Popen(['python3','-u',str(r/'finalize.py')],stdout=out,stderr=subprocess.STDOUT,env=env);(r/'finalize.pid').write_text(str(p.pid)+'\\n');assert p.wait()==0
  result={'status':'UNCHANGED_BENCHMARK_COMPLETE_AWAIT_LOCAL_EVIDENCE_REVIEW','nonce':sr['selected_nonce'],'scope':'No upload by this controller. Verify complete source/evidence, refresh current records and require strict actual Toffoli improvement before authorized official submission.'}
 else:result={'status':'DECLARED_NONCE_PREFIX_EXHAUSTED_PRESERVE_NO_BENCHMARK','scope':'No passing nonce, no benchmark/upload. Preserve frozen source, gate and every rejection.'}
 (r/'PIPELINE-RESULT.json').write_text(json.dumps(result,indent=2)+'\\n');(r/'pipeline.exit').write_text('0\\n')
except BaseException:
 (r/'pipeline.exit').write_text('1\\n');(r/'PIPELINE-ERROR.txt').write_text(traceback.format_exc());raise
''';(r/'run.py').write_text(driver)
launch='''import subprocess,json
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/breakthrough-recycle-final-20261021');assert not(r/'pipeline.pid').exists()
with(r/'pipeline.log').open('xb')as out:p=subprocess.Popen(['nohup','python3','-u',str(r/'run.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'pipeline.pid').write_text(str(p.pid)+'\\n');print(json.dumps({'pid':p.pid,'scope':'Wait for own first gate PASS, new exact engine qualification, ascending lowestnonce search, selected complete protected replay, unchanged benchmark. No upload until independent local source/evidence/strict-current-improvement review.'}))
''';(r/'launch.py').write_text(launch)
for folder in[n,r]:
 (folder/'.gitignore').write_text('candidate/\n__pycache__/\n*.jsonl\n');(folder/'.gitattributes').write_text('* -text\n');(folder/'PLAN.md').write_text('# Dependent exact qualification and benchmark\n\nOnly candidate207source own final32768x64 PASS permits fresh8nonce/24protected fullstate qualification and ascending1..65536/lowestPASS search. Unchanged original engine; all input/RNG/curve/quantum/classical/phase controls required. Only final IDENTITY_NONCE may change; exact entire pre-tail comparison and unchanged9024shot benchmark mandatory. Automatic official submission after complete independent local evidence/source review and strict current Toffoli improvement. Attribution GPT-6 sol/Codex.\n')
 subprocess.run(['ssh','-o','BatchMode=yes','smu_server','mkdir','/home/hclau/ecdsa_research/'+folder.name],check=True)
 for p in folder.iterdir():
  if p.suffix=='.py':compile(p.read_text(),str(p),'exec');subprocess.run(['scp','-o','BatchMode=yes',str(p),'smu_server:/home/hclau/ecdsa_research/'+folder.name+'/'+p.name],check=True)
out=subprocess.check_output(['ssh','-o','BatchMode=yes','smu_server','python3','/home/hclau/ecdsa_research/'+r.name+'/launch.py'],text=True);(r/'SERVER-LAUNCH.json').write_text(out);print(out)
