from pathlib import Path
import ast
a=Path(__file__).parent;s=(a/'collect-groups-context-final.py').read_text().replace('breakthrough-groups-context-final-20261020','breakthrough-depth12-final-20261020').replace('final native-both evidence/source member','final depth12 evidence/source member');ast.parse(s);(a/'collect-depth12-final.py').write_text(s);print('Depth12 complete evidence collector prepared.')
