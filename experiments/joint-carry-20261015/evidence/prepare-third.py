"""Third isolated attempt: explicit shift type for the U256 observer expression."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'prepare-second.py').read_text().replace('state2','state3')
exec(compile(s,str(root/'prepare-third.py'),'exec'))
