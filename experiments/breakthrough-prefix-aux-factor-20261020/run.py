import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;cases=json.loads((r/'AUX-CASES.json').read_text())['cases'];sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();results=[]
try:
 for index,case in enumerate(cases):
  child=r/('case'+str(index));child.mkdir();shutil.copyfile(r/'search-template.py',child/'search.py')
  for name in['PREFIX-DAG.json','FUNCTIONS.json']:shutil.copyfile(r/name,child/name)
  (child/'WINDOWS.json').write_text(json.dumps({'cases':[case]},indent=2)+'\n');(child/'SOURCE-FREEZE.json').write_text(json.dumps({p.name:sha(p)for p in child.iterdir()if p.is_file()},indent=2)+'\n')
  with(r/('case'+str(index)+'.log')).open('xb')as log:
   p=subprocess.Popen(['timeout','300','python3',str(child/'search.py')],cwd=child,stdout=log,stderr=subprocess.STDOUT);(r/('case'+str(index)+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
  (r/('case'+str(index)+'.exit')).write_text(str(rc)+'\n');assert rc==0;result=json.loads((child/'RESULT.json').read_text());results.append(result);(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\n');print(index,result['status'],flush=True)
  if result['solution']:break
 (r/'RESULT.json').write_text(json.dumps({'status':'RETAINED_AUXILIARY_FACTOR_SEARCH_NOT_NATIVE','cases':results},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
