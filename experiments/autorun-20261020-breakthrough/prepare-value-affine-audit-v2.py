from pathlib import Path
import ast
a=Path(__file__).parent
source=(a/'value-affine-audit.rs').read_text().replace('2_000_000','8_000_000')
(a/'value-affine-audit-v2.rs').write_text(source)
s=(a/'prepare-value-affine-audit.py').read_text().replace('breakthrough-value-affine-audit-20261020','breakthrough-value-affine-audit-v2-20261020').replace("a/'value-affine-audit.rs'","a/'value-affine-audit-v2.rs'").replace('2million','8million')
ast.parse(s)
exec(compile(s,str(a/'prepare-value-affine-audit.py'),'exec'))
