from pathlib import Path
import ast
a=Path(__file__).parent
names=['breakthrough-public-width1233-context65536-20261020','breakthrough-public-width-live-20261020','breakthrough-guarded-live-products-20261020','breakthrough-public-prefix27-width-v2-20261020','breakthrough-grouped-exact-resource-grid-20261020','breakthrough-public-width1232-context-20261020']
for src,dest,terminator in [('seal-research-cycle7.py','seal-research-cycle8.py','\nws='),('collect-research-cycle7.py','collect-research-cycle8.py','\nsha=')]:
 s=(a/src).read_text();start=s.index('names=[');end=s.index(terminator,start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/dest).write_text(s)
print('Six completed exact proof/native/failed-fixture fronts selected.')
