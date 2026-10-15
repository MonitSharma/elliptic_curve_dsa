"""Start only the bounded timing driver, detached with dedicated evidence."""
from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parent
assert str(root)=='/home/hclau/ecdsa_research/repair67-cost-20261016'
assert not (root/'run.pid').exists(), 'Preserve any earlier launch.'
available=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))
assert available>=148*1024*1024
with (root/'launch.log').open('w') as output:
 child=subprocess.Popen(['nohup','bash',str(root/'run.sh')],cwd=root,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
(root/'run.pid').write_text(str(child.pid)+'\n')
print(json.dumps({'pid':child.pid,'type':'cost-only; no nonce selection or search authority','threads':8,'memory_cap_GiB':48,'available_GiB':available/1024**2}))
