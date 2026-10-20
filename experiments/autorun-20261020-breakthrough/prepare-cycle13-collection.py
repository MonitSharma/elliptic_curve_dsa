from pathlib import Path
import ast
a=Path(__file__).parent;names=['breakthrough-public-best-drop-nonce-v2-20261020']
for src,dest,terminator in[('seal-research-cycle12.py','seal-research-cycle13.py','\nws='),('collect-research-cycle12.py','collect-research-cycle13.py','\nsha=')]:
 s=(a/src).read_text();start=s.index('names=[');end=s.index(terminator,start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/dest).write_text(s)
print('Completed finite65536nonce search selected; no continuation or benchmark.')
