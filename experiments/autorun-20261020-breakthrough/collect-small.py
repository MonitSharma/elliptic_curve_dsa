from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent;names=['breakthrough-prefix27-room-grid-20261020','breakthrough-prefix-xag-resynth-20261020'];s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+','.join(repr(n)for n in names)+',');(r/'collect-small-base.py').write_bytes(s.encode())
for name in names:
 subprocess.run(['scp',str(r/'seal-small.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-small.py'],check=True)
 subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-small.py {name}'],check=True)
 subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-small-base.py'),name],check=True)
