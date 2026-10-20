from pathlib import Path
import subprocess,sys
a=Path(__file__).parent;r=a.parent/'breakthrough-value-aig-audit-20261020';assert not(r/'solver-controller.pid').exists()
with(r/'solver-controller.log').open('xb')as log:p=subprocess.Popen([sys.executable,str(a/'solve-value-aig.py')],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32'else 0)
(r/'solver-controller.pid').write_text(str(p.pid)+'\n');print(p.pid)
