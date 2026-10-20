"""Set the required physical-cap environment for standalone native fixtures."""
import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'run.py').read_text();s=s.replace("r=Path(__file__).resolve().parent;t=r/'observer';","os.environ['PEBBLE_HARD_CAP']='1234'\nr=Path(__file__).resolve().parent;t=r/'observer';")
s=s.replace("run(['python3','prepare.py'],'prepare',r);", "assert(r/'run.exit').read_text().strip()=='1';")
s=s.replace("name='tests-'+str(i)","name='v2-tests-'+str(i)").replace("],'build');rows=[]", "],'build-v2');rows=[]").replace("r/'run.exit'", "r/'run-v2.exit'")
# The admission assertion still checks the original failed runner.
s=s.replace("assert(r/'run-v2.exit').read_text().strip()=='1'", "assert(r/'run.exit').read_text().strip()=='1'")
(r/'run-v2.py').write_bytes(s.encode());dest='smu_server:/home/hclau/ecdsa_research/breakthrough-prefix27-cleanup11-native-20261020/'
subprocess.run(['scp',str(r/'run-v2.py'),dest],check=True);subprocess.run(['ssh','smu_server','python3 /home/hclau/ecdsa_research/breakthrough-sparse-polynomial-20261020/launch-job.py breakthrough-prefix27-cleanup11-native-20261020 run-v2.py supervisor-v2'],check=True)
