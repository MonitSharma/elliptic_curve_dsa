from pathlib import Path
import shutil,ast
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-native-both-final-gate-20261020';r=root/'experiments/breakthrough-native-context-final-gate-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('__pycache__/\n*resource-preflight*\n');shutil.copyfile(old/'census.py',r/'census.py')
s=(old/'declare.py').read_text();changes={"c=ws/'breakthrough-native-both-finished-20261020'":"c=ws/'breakthrough-native-context-finished-v3-20261020'","predecessor=ws/'breakthrough-context-lease-final-20261020'":"predecessor=ws/'breakthrough-native-both-final-20261020'","c/'FINISHED-RESULT.json'":"c/'RESULT.json'","len(f['source_files'])==200":"len(f['source_files'])==201","a['native_tests']==27":"a['native_tests']==1","a['qubits']==1464":"a['qubits']==1480","a['diagnostic_weight']==748689.0":"a['diagnostic_weight']<748689.0",'native_both_finished.rs':'native_context_cache.rs',"a['native_stream_sha256']=='a871e42c3a40aa7fe228f68b8024a7167e57cdafbfd6732e19b650d2e6f845b9'":"a['stream_sha256']",'260b3ba0-d604-4f0d-9d55-934055d216b4':'d182a53e-be3d-4119-8298-303a9a9de07a',"{'qubits':1480,'toffoli':750705}":"{'qubits':1464,'toffoli':748691}",'1111043400':'1096083624',"pr['source_files']==198":"pr['source_files']==200",'d1f5e785f640fcf49a6af9b4a3b266c7aa3a61c3ef9387563c5ca6aadb9def9c':'cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536',"<750705":"<748691",'native-rail-g6-fixed-final-20261020-v1':'native-context499-exact-final-20261020-v1',"'workers_per_source':16":"'workers_per_source':8","'candidate_qubits_from_protected_analyzer':1464":"'candidate_qubits_from_protected_analyzer':1480"}
for x,y in changes.items():assert x in s,x;s=s.replace(x,y)
needle=";(r/'GATE-DECLARATION.json').write_text(json.dumps(d,indent=2)+'\\n');";assert s.count(needle)==1
extra=";dev=ws/'breakthrough-native-context-development-20261020';assert(dev/'DEVELOPMENT-CONTROLLER.exit').read_text().strip()=='0';d.update(development_plan_sha256=sha(dev/'PLAN.json'),development_result_sha256=sha(dev/'DIAGNOSTIC.json'),scope=f['scope'],verdict_policy='Sole finalgate for fixed499 exactcontext leases on officiald182.16 extra donor wires for independentT; no new precision/cut/window. Outcome final: no relabel, extension or nonce to reverse failure. All source/proof choices frozen before development.');"
s=s.replace(needle,extra+needle[1:]);ast.parse(s);(r/'declare.py').write_text(s)
(r/'run.py').write_text('''import json,os,shutil,socket,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
try:
 start=time.time();c=ws/'breakthrough-native-context-finished-v3-20261020';d=ws/'breakthrough-native-context-development-20261020'
 while not(c/'run.exit').exists()or not(d/'DEVELOPMENT-CONTROLLER.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(c/'run.exit').read_text().strip()=='0'and(d/'DEVELOPMENT-CONTROLLER.exit').read_text().strip()=='0';assert socket.gethostname()=='LHC-104-070'and os.cpu_count()>=64;available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024*1024;(r/'census-resource-preflight.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'cpus':os.cpu_count(),'mem_available_kib':available,'workers_total':16,'library_threads':1,'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{x:shutil.which(x)for x in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,pcpu,pmem,args','--sort=-pcpu']).decode()},indent=2)+'\\n');subprocess.run(['python3',str(r/'declare.py')],cwd=r,check=True);subprocess.run(['python3',str(r/'census.py')],cwd=r,check=True);(r/'controller.exit').write_text('0\\n')
except Exception:
 (r/'controller.exit').write_text('1\\n');raise
''')
(r/'PLAN.md').write_text('''# Sole final context499 T gate

Predeclared labelnative-context499-exact-final-20261020-v1,32768x64/source,
candidatefixednonce0, exact then-current officialT parentd182a53e/cec715. Refresh
public records immediately before declaration; stop without sampling if target
changes. Wait native source generation and512 fresh full-output development.
Eight census workers/source,16 total, resource preflight before execution.
All four AGENTS statistical criteria apply; verdict final, no resample/relabel/
extension/nonce to reverse failure. Only PASS permits qualifiedascendingnonce,
unchangedbenchmark, complete local evidence review and automaticGPT-6sol/Codex
submission. Extra16 wires allowed for independentT objective; no product claim.
''');print(r)
