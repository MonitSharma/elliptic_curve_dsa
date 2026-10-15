#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/rail-tail64-20261016
echo $$ > controls.pid
trap 'echo $? > controls.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > controls-preflight.json
ulimit -v 16777216
python3 - <<'PY'
from pathlib import Path
p=Path('rail8_tail64.c');s=p.read_text()
needle='return _mm512_srav_epi64(_mm512_sllv_epi64(a,cn(n)),cn(n));'
assert s.count(needle)==1
Path('rail8_tail64_wrongshift.c').write_text(s.replace(needle,'return _mm512_srlv_epi64(_mm512_sllv_epi64(a,cn(n)),cn(n));'))
PY
/usr/bin/time -v gcc -O3 -march=native -fPIC -shared rail8_tail64_wrongshift.c -o librail8_tail64_wrongshift.so > controls-build.log 2>&1
/usr/bin/time -v python3 extra_controls.py > controls.log 2>&1
