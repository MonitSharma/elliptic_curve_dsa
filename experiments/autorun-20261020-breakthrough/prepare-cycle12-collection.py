from pathlib import Path
import ast
a=Path(__file__).parent;names=['breakthrough-exact-witness-ripple-v2-20261020']
for src,dest,terminator in[('seal-research-cycle11.py','seal-research-cycle12.py','\nws='),('collect-research-cycle11.py','collect-research-cycle12.py','\nsha=')]:
 s=(a/src).read_text();start=s.index('names=[');end=s.index(terminator,start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/dest).write_text(s)
print('Completed native-failed v2 source and controls selected; active v3 excluded.')
