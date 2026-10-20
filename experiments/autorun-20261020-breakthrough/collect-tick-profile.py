import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;name='breakthrough-prefix-tick-profile-20261020';s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+repr(name)+',');(r/'collect-tick-profile-base.py').write_text(s)
subprocess.run(['scp',str(r/'seal-tick-profile.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-tick-profile.py'],check=True);subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-tick-profile.py'],check=True);subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-tick-profile-base.py'),name],check=True)
