from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'prepare-public1829-width-port.py').read_text().replace('breakthrough-public1829-width-port-20261020','breakthrough-public1829-width-port-v2-20261020')
s=s.replace("raw=raw.replace(needle,needle+b'\\nif std::env::var(\"STACK_WIDTH_RESEARCH\").is_ok_and(|s|s!=\"public\"){", "raw=raw.replace(needle,b'pub(super) fn run(mut v:Vec<Op>,resource_changed:bool)->Vec<Op>{\\nif resource_changed{")
needle='p.write_bytes(raw)\n\'\'\''
assert s.count(needle)==1
s=s.replace(needle,"p.write_bytes(raw)\np=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'ops = stream_edits::run(ops);';assert raw.count(needle)==1;raw=raw.replace(needle,b'ops = stream_edits::run(ops,config.is_some());');p.write_bytes(raw)\n'''" )
assert 'if resource_changed{'in s
ast.parse(s)
exec(compile(s,str(a/'prepare-public1829-width-port.py'),'exec'))
