import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;names=['breakthrough-prefix-tick-mixed-20261020','breakthrough-prefix-tick-alloc-20261020'];s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+','.join(repr(n)for n in names)+',');(r/'collect-mixed-allocation-base.py').write_text(s)
for name in names:
 subprocess.run(['scp',str(r/'seal-mixed-allocation.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-mixed-allocation.py'],check=True);subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-mixed-allocation.py {name}'],check=True);subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-mixed-allocation-base.py'),name],check=True)
