from pathlib import Path
import ast
a=Path(__file__).parent;s=(a/'prepare-groups-safe-official-checks.py').read_text();s=s.replace('breakthrough-groups-safe-final-20261020','breakthrough-groups-context-final-20261020').replace('len(paths)==204','len(paths)==205').replace('748184-b[','747453-b[');ast.parse(s);exec(compile(s,str(__file__),'exec'))
