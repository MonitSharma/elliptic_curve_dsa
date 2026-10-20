from pathlib import Path
import shutil
a=Path(__file__).parent;r=a.parent/'breakthrough-normalized-wrongpoint-check-20261020';r.mkdir(exist_ok=False);shutil.copyfile(a/'check-normalized-wrongpoint.py',r/'run.py');(r/'.gitignore').write_text('__pycache__/\n');(r/'.gitattributes').write_text('* -text\n');print(r.name)
