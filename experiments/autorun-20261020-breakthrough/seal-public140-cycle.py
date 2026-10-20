import hashlib,json,subprocess
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research')
groups={
 'seal-width-cycle.py':['breakthrough-wide-generic-20261020','breakthrough-wide-square-budget-20261020','breakthrough-wide-uniform-compare-20261020','breakthrough-spacious-budget-20261020','breakthrough-primed-pool-20261020','breakthrough-public-schedule-20261020'],
 'seal-wide-diagnostics.py':['breakthrough-spacious-correctness-20261020','breakthrough-public140-correctness-20261020'],
}
for script,names in groups.items():
 for name in names:
  if (ws/name/'EVIDENCE-MANIFEST.json').exists():
   receipt=json.loads((ws/name/'PACKAGE-RESULT.json').read_text())
   assert hashlib.sha256((ws/name/'evidence.tar.gz').read_bytes()).hexdigest()==receipt['archive_sha256']
   print(name,'existing seal verified',flush=True)
   continue
  subprocess.run(['python3',str(ws/script),name],check=True)
