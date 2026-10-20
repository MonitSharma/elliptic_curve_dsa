import json,re,sys
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research')
for name in sys.argv[1:]:
 assert re.fullmatch(r'[a-z0-9-]+',name);r=ws/name;result={'name':name,'exits':{p.name:p.read_text().strip()for p in r.glob('run*.exit')},'tests':{p.name:[int(n)for n in re.findall(r'test result: ok\. (\d+) passed; 0 failed;',p.read_text())]for p in r.glob('tests*.log')}}
 p=r/'ADMISSION-PROGRESS.json'
 if p.exists():result['cases']=[{k:v for k,v in row.items()if k in['cap','exit','raw_sha256','builder_totals']}for row in json.loads(p.read_text())]
 print(json.dumps(result),flush=True)
