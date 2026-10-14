from pathlib import Path
import subprocess
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits')
for name in ['diag2379-base','diag2379v2-n275-v2','diag2379v2-headflag-v1','diag2379v2-n274-v4']:
    (r/'evidence'/(name+'.patch')).write_bytes(subprocess.check_output(['git','-C',str(r/name),'diff','HEAD','--','src/point_add/']))
