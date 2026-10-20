from pathlib import Path
import shutil
a=Path(__file__).parent;r=a.parent/'breakthrough-sat-proof-check-ram-20261020';r.mkdir(exist_ok=False);shutil.copyfile(a/'run-ram-proof-check.py',r/'run.py');(r/'.gitignore').write_text('__pycache__/\n');(r/'.gitattributes').write_text('* -text\n')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-sat-proof-check-ram-20261020
python3 run.py
'''.replace('BASE',base)).encode());(r/'PLAN.md').write_text('''# Recheck the same solver proof using RAM-backed anonymous files

Kissat produced UNSAT on one fixed source/input; initial180s DRAT-trim check
timed out, so result remains INCONCLUSIVE. No solver rerun/input/circuit change.
Verify original CNF/proof/binary/source hashes, copy identical bytes into Linux
anonymous memfd objects (no filesystem outsideworkspace), and independently
check the SAME proof with line-buffered progress and900s budget/6GiBaddress cap.
Require >=8GiBavailable memory before copying. Anonymous copies closed afterward.
Only DRAT-trim VERIFIED plus exit0 establishes certificate; otherwise unknown.
No statistical gate rerun/extension, nonce screen/rejection or quantumrecord.
''');print(r.name)
