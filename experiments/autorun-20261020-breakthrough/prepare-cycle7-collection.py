from pathlib import Path
import ast
a=Path(__file__).parent
names=['breakthrough-public-acd0-exact-width-v2-20261020','breakthrough-public-width1233-context-20261020','breakthrough-public-prefix27-width-20261020','breakthrough-public-width1233-development-20261020']
for src,dest,terminator in [('seal-research-cycle6.py','seal-research-cycle7.py','\nws='),('collect-research-cycle6.py','collect-research-cycle7.py','\nsha=')]:
 s=(a/src).read_text();start=s.index('names=[');end=s.index(terminator,start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/dest).write_text(s)
print('Four completed exact-width/proof/development fronts selected.')
