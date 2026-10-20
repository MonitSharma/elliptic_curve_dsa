from pathlib import Path
import ast
a=Path(__file__).parent
names=['breakthrough-value-dominance-audit-20261020','breakthrough-value-boolean-reset-audit-20261020']
for original,dest,terminator in [('seal-research-cycle12.py','seal-post-outage.py','\nws='),('collect-research-cycle13.py','collect-post-outage.py','\nsha=')]:
 s=(a/original).read_text();start=s.index('names=[');end=s.index(terminator,start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/dest).write_text(s)
print('Two completed pre-outage verifier-only fronts selected; no restart or gate/nonce work.')
