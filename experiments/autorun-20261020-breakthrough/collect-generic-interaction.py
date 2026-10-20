import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;name='breakthrough-prefix27-generic-interaction-20261020';s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+repr(name)+',');(r/'collect-generic-interaction-base.py').write_text(s)
subprocess.run(['scp',str(r/'seal-generic-interaction.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-generic-interaction.py'],check=True);subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-generic-interaction.py'],check=True);subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-generic-interaction-base.py'),name],check=True)
