from pathlib import Path
import ast
a=Path(__file__).parent
names=['breakthrough-public-expanded-cap-20261020','breakthrough-public-drop-tradeoffs-20261020','breakthrough-public-rmin-context-20261020','breakthrough-public-rmin-finished-20261020','breakthrough-value-cone-audit-20261020','breakthrough-value-cone-audit-v2-20261020']
for src,dest,terminator in [('seal-research-cycle8.py','seal-research-cycle9.py','\nws='),('collect-research-cycle8.py','collect-research-cycle9.py','\nsha=')]:
 s=(a/src).read_text();start=s.index('names=[');end=s.index(terminator,start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/dest).write_text(s)
print('Six completed resource, bound-source and read-only-audit fronts selected.')
