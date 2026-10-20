from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent;names=['breakthrough-prefix-factor-chain-20261020','breakthrough-prefix-factor-complete-20261020','breakthrough-prefix-aux-factor-20261020','breakthrough-prefix-fusion-20261020','breakthrough-prefix-fusion-all-20261020','breakthrough-public322-square-grid-20261020'];s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+','.join(repr(n)for n in names)+',');(r/'collect-next-cycle-base.py').write_bytes(s.encode())
for name in names:
 script='seal-continuation.py'if name.endswith('square-grid-20261020')else'seal-small.py'
 subprocess.run(['scp',str(r/script),f'smu_server:/home/hclau/ecdsa_research/{name}/{script}'],check=True)
 subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/{script} {name}'],check=True)
 subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-next-cycle-base.py'),name],check=True)
