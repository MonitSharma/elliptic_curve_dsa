from pathlib import Path
root=Path(__file__).resolve().parent
(root/'run-third.sh').write_text((root/'run-second.sh').read_text().replace('state2','state3').replace('prepare-second.py','prepare-third.py'),newline='\n')
