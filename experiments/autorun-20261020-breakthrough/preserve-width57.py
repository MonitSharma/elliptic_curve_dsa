"""Seal both native width57 grids, retaining the environment-binding failure."""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent
s=(r/'seal-exact154-cycle.py').read_text()
s=s.replace("config={", "config={\n 'breakthrough-prefix27-width57-20261020':('observer','SOURCE_FREEZE-v2.json','run-v2.exit',{'tests-'+str(i)+'.log':[v] for i,v in enumerate([2,2,2,1,1,1,1,1,1,1,1,1,3,1,4,3,2,3,1,1])}),")
s=s.replace("'ADMISSION-RESULT.json']", "'ADMISSION-RESULT.json','ADMISSION-RESULT-v2.json']")
(r/'seal-width57.py').write_bytes(s.encode())
s=(r/'collect-exact154-cycle.py').read_text().replace("allowed=[", "allowed=['breakthrough-prefix27-width57-20261020',")
(r/'collect-width57.py').write_bytes(s.encode())
subprocess.run(['scp',str(r/'seal-width57.py'),'smu_server:/home/hclau/ecdsa_research/breakthrough-prefix27-width57-20261020/seal-width57.py'],check=True)
subprocess.run(['ssh','smu_server','python3 /home/hclau/ecdsa_research/breakthrough-prefix27-width57-20261020/seal-width57.py breakthrough-prefix27-width57-20261020'],check=True)
subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-width57.py'),'breakthrough-prefix27-width57-20261020'],check=True)
