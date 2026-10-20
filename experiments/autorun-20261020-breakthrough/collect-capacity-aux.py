from pathlib import Path
import ast,subprocess
r=Path(__file__).resolve().parent;names=['breakthrough-public322-capacity-grid-20261020','breakthrough-prefix-fresh-aux-20261020']
s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+','.join(repr(x)for x in names)+',');ast.parse(s);(r/'collect-capacity-aux-base.py').write_text(s)
for name in names:
 subprocess.run(['scp',str(r/'seal-capacity-aux.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-capacity-aux.py'],check=True)
 subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-capacity-aux.py {name}'],check=True)
 subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-capacity-aux-base.py'),name],check=True)
