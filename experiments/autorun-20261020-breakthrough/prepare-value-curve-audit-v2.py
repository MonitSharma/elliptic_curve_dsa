from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'prepare-value-curve-audit.py').read_text().replace('breakthrough-value-curve-audit-20261020','breakthrough-value-curve-audit-v2-20261020').replace('a:0u64.into()','a:"0x0".parse().unwrap()').replace('b:7u64.into()','b:"0x7".parse().unwrap()').replace('2u64.into()','"0x2".parse().unwrap()')
ast.parse(s)
failure=a.parent/'breakthrough-value-curve-audit-20261020/SETUP-FAILURE.txt'
failure.write_text('Original native compilation failed before any curve fixture: ruint U256 lacks the u64 Into trait. Frozen source and compiler errors preserved. V2 uses typed-inferred hexadecimal parsing, matching the protected reference constructor. No gate, nonce or scored result.\n')
exec(compile(s,str(a/'prepare-value-curve-audit.py'),'exec'))
