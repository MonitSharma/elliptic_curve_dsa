from pathlib import Path
import ast,subprocess
r=Path(__file__).resolve().parent
names=['breakthrough-public322-square-generic-20261020','breakthrough-public322-square-lease-20261020','breakthrough-public322-square-finished-20261020','breakthrough-public322-square-final-gate-20261020']
s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+','.join(repr(x)for x in names)+',');ast.parse(s);(r/'collect-square-cycle-base.py').write_text(s)
for name in names:
 subprocess.run(['scp',str(r/'seal-square-cycle.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-square-cycle.py'],check=True)
 subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-square-cycle.py {name}'],check=True)
 subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-square-cycle-base.py'),name],check=True)
