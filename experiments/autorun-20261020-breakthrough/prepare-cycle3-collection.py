import ast
from pathlib import Path
a=Path(__file__).parent;tree=ast.parse((a/'seal-research-cycle3.py').read_text());names=ast.literal_eval(next(x.value for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='names'for t in x.targets)));s=(a/'collect-research-cycle2.py').read_text();start=s.index('names=[');end=s.index('\nsha=',start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/'collect-research-cycle3.py').write_text(s);print(len(names),'fronts')
