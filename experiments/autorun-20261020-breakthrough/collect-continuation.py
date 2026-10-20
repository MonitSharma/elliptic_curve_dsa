from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent
s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=[\'breakthrough-exact-branch-alias-20261020\',\'breakthrough-prefix27-selective-20261020\',')
(r/'collect-continuation-base.py').write_bytes(s.encode())
for name in ['breakthrough-exact-branch-alias-20261020','breakthrough-prefix27-selective-20261020']:
 subprocess.run(['scp',str(r/'seal-continuation.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-continuation.py'],check=True)
 subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-continuation.py {name}'],check=True)
 subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-continuation-base.py'),name],check=True)
