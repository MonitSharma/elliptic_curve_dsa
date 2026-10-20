from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'prepare-local-public1829-port-v2.py').read_text().replace('breakthrough-public1829-width-port-local-v2-20261020','breakthrough-public1829-width-port-local-v3-20261020').replace("old=ex/'breakthrough-public1829-width-port-20261020'","old=ex/'breakthrough-public1829-width-port-v2-20261020'")
ast.parse(s)
exec(compile(s,str(a/'prepare-local-public1829-port-v2.py'),'exec'))
