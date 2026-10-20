from pathlib import Path
import ast
a=Path(__file__).parent
(a/'global-prefix-simplify-v3.rs').write_text((a/'global-prefix-simplify.rs').read_text().replace('bad.apply_iter(fault);','bad.apply_iter(fault.iter());'))
s=(a/'prepare-global-prefix-component.py').read_text().replace('breakthrough-global-prefix-component-20261020','breakthrough-global-prefix-component-v3-20261020').replace(".replace('name=\"product_pareto_discover\"','name=\"global_prefix_simplify\"')",".replace('product_pareto_discover','global_prefix_simplify')").replace("assert'name=\"global_prefix_simplify\"'in","assert'global_prefix_simplify'in").replace("a/'global-prefix-simplify.rs'","a/'global-prefix-simplify-v3.rs'")
ast.parse(s)
old=a.parent/'breakthrough-global-prefix-component-v2-20261020';(old/'NATIVE-COMPILATION-FAILURE.txt').write_text('Native test compilation stopped before any stream input: protected Simulator::apply_iter requires an Iterator, not a slice, in the deliberate-fault branch. Frozen source and compiler diagnostics retained. V3 changes only that cfg(test) call to fault.iter(); production simplifier unchanged. No gate/nonce/resource result.\n')
exec(compile(s,str(a/'prepare-global-prefix-component.py'),'exec'))
