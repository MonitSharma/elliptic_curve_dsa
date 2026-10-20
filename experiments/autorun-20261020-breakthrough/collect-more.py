from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parent
names=['breakthrough-prefix27-cleanup11-native-20261020','breakthrough-public54fc-lease-20261020','breakthrough-wide-tight-color-20261020','breakthrough-public8b-lease-20261020']
s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[','allowed=['+','.join(repr(n)for n in names)+',');(r/'collect-more-base.py').write_bytes(s.encode())
for name in sys.argv[1:]:
 assert name in names
 subprocess.run(['scp',str(r/'seal-continuation.py'),f'smu_server:/home/hclau/ecdsa_research/{name}/seal-continuation.py'],check=True)
 subprocess.run(['ssh','smu_server',f'python3 /home/hclau/ecdsa_research/{name}/seal-continuation.py {name}'],check=True)
 subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-more-base.py'),name],check=True)
