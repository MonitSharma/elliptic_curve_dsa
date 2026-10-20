from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent;s=(r/'collect-exact154-final.py').read_text().replace('breakthrough-public140-exact154-final-20261020','breakthrough-public8b-repeat-final-20261020').replace("Complete local benchmark reproduction; queued, not officially evaluated.","Complete local benchmark reproduction, ready for authorized automatic submission; not officially evaluated.")
(r/'collect-repeat-final-base.py').write_bytes(s.encode());subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-repeat-final-base.py')],check=True)
