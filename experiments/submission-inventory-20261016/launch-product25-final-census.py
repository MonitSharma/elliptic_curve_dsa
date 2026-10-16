"""Launch the existing predeclared cohort once, without changing its inputs."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path('/home/hclau/ecdsa_research/product25-final-20261016')
assert (root / 'final.exit').read_text().strip() == '0'
assert not (root / 'final-census.pid').exists()
assert not (root / 'final-fresh').exists()
assert hashlib.sha256((root / 'final-census.py').read_bytes()).hexdigest() == 'ca07e011727f380447d6e8b70619266c2f4c8af764824d314ff63bbbec41f4ce'
expected = '''#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product25-final-20261016
test ! -e final-census.pid
test "$(cat final.exit)" = 0
echo $$ > final-census.pid
trap 's=$?; echo "$s" > final-census.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 50331648
printf '%s  final-census.py\\n' ca07e011727f380447d6e8b70619266c2f4c8af764824d314ff63bbbec41f4ce | sha256sum --check -
timeout 5400 python3 final-census.py 93122ce2668fe2861eba894b1520d3e44552c2094487337dd92300c2aa9d57d2
'''
assert (root / 'run-final-census.sh').read_text() == expected
result = json.loads((root / 'BENCHMARK_RESULT.json').read_text())
assert result['status'] == 'UNCHANGED_BENCHMARK_PASS'
assert result['product'] == 939285014
with (root / 'final-census.log').open('x') as log:
    proc = subprocess.Popen(['nohup', 'bash', str(root / 'run-final-census.sh')], cwd=root,
                            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True)
(root / 'final-census-launch.pid').write_text(str(proc.pid) + '\n')
print(json.dumps(dict(pid=proc.pid, log=str(root / 'final-census.log'), workers=8)))
