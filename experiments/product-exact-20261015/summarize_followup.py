import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parent
names=['follow-chain-20261016','scratch-v2-20261016','unfold-20261016','pair-expansion-20261016','flags-chain-20261016','flags-four-20261016','flags-extended-20261016']
summary={}
for name in names:
    source=root/name
    if not source.exists():continue
    row={'launcher_exit':(source/'launcher.exit').read_text().strip() if (source/'launcher.exit').exists() else None,'packets':{},'generations':{}}
    for path in sorted(source.glob('*.log')):
        data=path.read_text(errors='replace')
        for line in data.splitlines():
            if line.startswith('DIAGNOSTIC_ONLY '):
                row['packets'][path.name]=dict(re.findall(r'(\w+)=(\S+)',line))
            elif line.startswith('LAZY_SUMMARY '):
                item=dict(re.findall(r'(\w+)=(\S+)',line));item['distinct_donors']=len(set(re.findall(r'donor=(\d+)',data)));row['generations'][path.name]=item
    summary[name]=row
(root/'followup-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
