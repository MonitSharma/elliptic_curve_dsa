from pathlib import Path
a=Path(__file__).parent
s=(a/'collect-exact-witness-final.py').read_text().replace('breakthrough-exact-witness-final-20261020','breakthrough-de8-repeat-final-20261020').replace('205','206')
exec(compile(s,str(a/'collect-exact-witness-final.py'),'exec'))
