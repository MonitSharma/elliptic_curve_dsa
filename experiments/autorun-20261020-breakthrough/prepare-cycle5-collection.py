from pathlib import Path
import ast
a=Path(__file__).parent;names=['breakthrough-grouped-compact-width-v7-20261020','breakthrough-grouped-compact-width-v8-20261020','breakthrough-grouped-compact-width-v9-20261020','breakthrough-zero-lifetime-audit-20261020']
s=(a/'seal-research-cycle3.py').read_text();start=s.index('names=[');end=s.index('\nws=',start);s=s[:start]+'names='+repr(names)+s[end:]
needle="audit={'status':";assert s.count(needle)==1;s=s.replace(needle,"audit={'ineligible_selector_mismatch':name in ['breakthrough-grouped-compact-width-v7-20261020','breakthrough-grouped-compact-width-v8-20261020'],'status':")
ast.parse(s);(a/'seal-research-cycle5.py').write_text(s)
s=(a/'collect-research-cycle3.py').read_text();start=s.index('names=[');end=s.index('\nsha=',start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/'collect-research-cycle5.py').write_text(s);print('Four completed fronts; ineligible selector attempts explicitly flagged.')
