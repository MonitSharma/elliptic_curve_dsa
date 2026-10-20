from pathlib import Path
import shutil
a=Path(__file__).parent;r=a.parent/'breakthrough-sat-proof-tools-20261020';r.mkdir(exist_ok=False);(r/'.gitignore').write_text('tool-repos/\n__pycache__/\n*.drat\n');(r/'.gitattributes').write_text('* -text\n')
shutil.copyfile(a/'run-sat-proof-tools.py',r/'run.py')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-sat-proof-tools-20261020
export OMP_NUM_THREADS=1
python3 run.py
'''.replace('BASE',base)).encode());(r/'launch-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-sat-proof-tools-20261020
test ! -e run.pid
nohup setsid sh run-local.sh > run.log 2>&1 < /dev/null &
printf '%s\\n' "$!" > run.pid
cat run.pid
'''.replace('BASE',base)).encode())
(r/'PLAN.md').write_text('''# Isolated SAT solver and independent proof-checker qualification

Official repositories https://github.com/arminbiere/kissat and
https://github.com/marijnheule/drat-trim, source commits/whole tracked hashes
frozen BEFORE compiling. Workspace-only clones/builds, two build threads,
one solver/checker thread, bounded memory/time/file sizes. Native solver tests
and separate SAT/UNSAT/invalid-proof controls precede fixed-source main CNF.
Same ONE Boolean input model/source6192 and same original CNF already qualified
24native/27protected controls; Z3's2GiB parse failure stays inconclusive.
Any UNSAT requires independent DRAT-trim VERIFIED. No nonce rejection, source/
gate/census change, quantum resource result or challenge submission.
''');print(r.name)
