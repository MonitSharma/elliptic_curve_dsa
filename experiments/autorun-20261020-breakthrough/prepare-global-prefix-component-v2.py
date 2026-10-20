from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'prepare-global-prefix-component.py').read_text().replace('breakthrough-global-prefix-component-20261020','breakthrough-global-prefix-component-v2-20261020').replace(".replace('name=\"product_pareto_discover\"','name=\"global_prefix_simplify\"')",".replace('product_pareto_discover','global_prefix_simplify')").replace("assert'name=\"global_prefix_simplify\"'in","assert'global_prefix_simplify'in")
ast.parse(s)
old=a.parent/'breakthrough-global-prefix-component-20261020';(old/'.gitignore').write_text('local-tool/\n');(old/'.gitattributes').write_text('* -text\n');(old/'SETUP-FAILURE.txt').write_text('Preparation stopped before source freeze/native tests because Cargo target name has spaces around equals. Partial verification source retained. Corrected separatev2 replaces the target name independent of whitespace. Foreground launch had no run-local.sh and did no computation. No circuit/gate/nonce result.\n')
exec(compile(s,str(a/'prepare-global-prefix-component.py'),'exec'))
