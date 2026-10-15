from pathlib import Path
root=Path(__file__).resolve().parent
(root/'run-fourth.sh').write_text((root/'run-second.sh').read_text().replace('state2','state4').replace('prepare-second.py','prepare-fourth.py'),newline='\n')
