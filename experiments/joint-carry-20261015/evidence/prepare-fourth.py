"""Raw random-read alignment includes both Hmr and R; preserve the prior attempt."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'prepare-second.py').read_text().replace('state2','state4')
exec(compile(s,str(root/'prepare-fourth.py'),'exec'))
