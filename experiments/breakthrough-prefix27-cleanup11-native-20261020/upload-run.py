from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-prefix27-selective-20261020'
s=(old/'run.py').read_text();s=s.replace("filters=['selective_room_tests'", "filters=['prefix_window_policy_tests','prefix27_full_fold_tests','selective_room_tests'").replace('counts==[1,2,2,1,1,2]','counts==[1,1,1,2,2,1,1,2]');s=s.replace("BREAK_CAP='1234',BREAK_HARD=str(case['cap'])","BREAK_CAP='1234',BREAK_PREFIX27_WINDOWS=case['windows'],BREAK_HARD=str(case['cap'])");s=s.replace("'SELECTIVE_PREFIX27_RAW_GRID_NOT_SCORED'","'CLEANUP11_NATIVE_AND_RAW_GRID_NOT_SCORED'");(r/'run.py').write_bytes(s.encode())
dest='smu_server:/home/hclau/ecdsa_research/breakthrough-prefix27-cleanup11-native-20261020/'
subprocess.run(['ssh','smu_server','mkdir /home/hclau/ecdsa_research/breakthrough-prefix27-cleanup11-native-20261020'],check=True);subprocess.run(['scp',str(r/'prepare.py'),str(r/'run.py'),dest],check=True);subprocess.run(['ssh','smu_server','python3 /home/hclau/ecdsa_research/breakthrough-sparse-polynomial-20261020/launch-job.py breakthrough-prefix27-cleanup11-native-20261020 run.py supervisor'],check=True)
