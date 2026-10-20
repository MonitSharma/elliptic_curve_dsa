from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'run-sat-proof-tools-v4.py').read_text();needle="run(['make','-j2'],'build-drat',drat,timeout=180);";assert s.count(needle)==1;s=s.replace(needle,"run(['gcc','-D_DEFAULT_SOURCE','-std=c99','-O2',str(drat/'drat-trim.c'),'-o',str(drat/'drat-trim')],'build-drat-default-source',drat,timeout=180);")
s=s.replace("'drat_trim_sha256':sha(checker),'tool_source_freeze_sha256'","'drat_trim_sha256':sha(checker),'checker_build_flags':'gcc -D_DEFAULT_SOURCE -std=c99 -O2; expose POSIX getc_unlocked, no source edit','tool_source_freeze_sha256'")
ast.parse(s);(a/'run-sat-proof-tools-v5.py').write_text(s)
s=(a/'prepare-sat-proof-tools.py').read_text().replace('breakthrough-sat-proof-tools-20261020','breakthrough-sat-proof-tools-v5-20261020').replace("a/'run-sat-proof-tools.py'","a/'run-sat-proof-tools-v5.py'").replace('Native solver tests','SAT solving-kernel tests; full CLI signal suite failure retained separately')
ast.parse(s)
exec(compile(s,str(a/'prepare-sat-proof-tools.py'),'exec'))
