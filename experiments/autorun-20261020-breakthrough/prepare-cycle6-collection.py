from pathlib import Path
import ast

a=Path(__file__).parent
names=['breakthrough-targeted-ripple-width-20261020','breakthrough-targeted-ripple-width-v2-20261020','breakthrough-public-acd0-reproduction-20261020','breakthrough-public-acd0-exact-width-20261020']
s=(a/'seal-research-cycle5.py').read_text();start=s.index('names=[');end=s.index('\nws=',start);s=s[:start]+'names='+repr(names)+s[end:]
s=s.replace("['candidate','observer']","['candidate','observer','parent']")
s=s.replace("for p in list(r.glob('*.ops.bin'))", "for p in list(r.glob('parent/ops.bin'))+list(r.glob('*.ops.bin'))")
ast.parse(s);(a/'seal-research-cycle6.py').write_text(s)
s=(a/'collect-research-cycle5.py').read_text();start=s.index('names=[');end=s.index('\nsha=',start);s=s[:start]+'names='+repr(names)+s[end:]
s=s.replace("['observer/','candidate/'", "['parent/','observer/','candidate/'")
ast.parse(s);(a/'collect-research-cycle6.py').write_text(s)
print('Four completed fronts selected; exact public reproduction included.')
