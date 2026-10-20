import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;name='breakthrough-prefix-retained-cleanup-20261020';s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+repr(name)+',');(r/'collect-retained-cleanup-base.py').write_text(s)
subprocess.run(['scp',str(r/'seal-retained-cleanup.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-retained-cleanup.py'],check=True);subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-retained-cleanup.py'],check=True);subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-retained-cleanup-base.py'),name],check=True)
