from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'run.sh').read_text().replace('observer','fold').replace('"$root/prepare.py"','"$root/prepare-fold.py"')
(root/'run-fold.sh').write_text(s,newline='\n')
