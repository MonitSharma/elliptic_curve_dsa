"""Use an existing1.93 build cache; original older job used a shared target."""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent;s=(r/'run.py').read_text();a="assert not t.exists();t.mkdir()\n for name in ['Cargo.toml','Cargo.lock','tight_color.rs','io.rs']:shutil.copyfile(old/name,t/name)\n subprocess.run(['cp','-a','--reflink=auto',str(old/'target'),str(t/'target')],check=True);";assert a in s
s=s.replace(a,"assert t.exists()and(r/'run.exit').read_text().strip()=='1'\n subprocess.run(['cp','-a','--reflink=auto',str(ws/'breakthrough-public54fc-lease-20261020/tool/target'),str(t/'target')],check=True);")
s=s.replace("(r/'run.exit').write_text", "(r/'run-v2.exit').write_text")
(r/'run-v2.py').write_bytes(s.encode());dest='smu_server:/home/hclau/ecdsa_research/breakthrough-wide-tight-color-20261020/'
subprocess.run(['scp',str(r/'run-v2.py'),dest],check=True);subprocess.run(['ssh','smu_server','python3 /home/hclau/ecdsa_research/breakthrough-sparse-polynomial-20261020/launch-job.py breakthrough-wide-tight-color-20261020 run-v2.py supervisor-v2'],check=True)
