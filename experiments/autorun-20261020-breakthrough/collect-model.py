from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent;s=(r/'collect-exact154-cycle.py').read_text().replace('allowed=[',"allowed=['breakthrough-prefix27-oneand-20261020',");(r/'collect-model-base.py').write_bytes(s.encode());subprocess.run([str(Path('.venv-research/Scripts/python.exe').resolve()),str(r/'collect-model-base.py'),'breakthrough-prefix27-oneand-20261020'],check=True)
