"""Correct admission order without editing any registered or live source."""
from pathlib import Path
import json,shutil
ws=Path(__file__).resolve().parent.parent;old=ws/'product-linear-witness-controls-20261020';r=ws/'product-linear-witness-controls-v2-20261020'
assert not r.exists() and (old/'run.exit').read_text().strip()=='1' and not (old/'build-tests.log').exists();r.mkdir()
for p in old.iterdir():
 if p.suffix in ['.rs','.py','.sh'] or p.name=='BINDING.json':shutil.copy2(p,r/p.name)
p=r/'run.py';s=p.read_text();limits="os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))"
assert s.count(limits)==1;s=s.replace(limits+'\n','')
needle="compiler=next(p for p in b['compiler_and_direct_dependencies']";assert s.count(needle)==1;s=s.replace(needle,limits+'\n'+needle);p.write_text(s,newline='\n')
p=r/'run.sh';p.write_text(p.read_text().replace('product-linear-witness-controls-20261020','product-linear-witness-controls-v2-20261020'),newline='\n')
(r/'ADMISSION-REPAIR.json').write_text(json.dumps({'status':'GLOBAL_RESOURCE_CHECK_BEFORE_ONE_CPU_AFFINITY','old_directory':str(old),'old_run_exit':1,'compiler_or_tests_started_in_old_attempt':False,'source_circuit_and_primitive_tests_unchanged':True,'why':'Profile compares global load to available affinity. Pinning the Python parent first reduced its inherited affinity to one CPU, making the global capacity guard refuse before compilation. Run the unchanged guard before pinning actual compile/test work to one CPU. Old source/descriptor/failed log preserved unchanged.'},indent=2)+'\n')
print('Prepared v2 admission-order correction; source/tests unchanged, old attempt preserved')
