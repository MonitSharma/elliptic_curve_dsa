"""Independent Toffoli tradeoff control: a larger dynamic arithmetic budget."""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;dest=root/'cap1536-b3';assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root/'unseeded-b3'
for rel in subprocess.check_output(['git','-C',str(source),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((source/rel).read_bytes())
p=dest/'src/point_add/leapfrog.rs';s=p.read_text();needle='("HEO_PIN_PP_WALK_MAX_QUBITS", "1267")';assert s.count(needle)==1;s=s.replace(needle,'("HEO_PIN_PP_WALK_MAX_QUBITS", "1536")');p.write_text(s)
(root/'cap1536.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'cap1536-manifest.json').write_text(json.dumps({'score':None,'revision':rev,'scope':'One predeclared width-for-Toffoli control at cap1536, starting from the unseeded terminal candidate. No rail table, comparison-window policy, packet, nonce or protected-source changes beyond that inherited candidate.','changed_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n')
