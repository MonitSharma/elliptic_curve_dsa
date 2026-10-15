#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/repair67-conditional-filter-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run.exit"' EXIT
test ! -e run.exit
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 25165824
python3 prepare.py > prepare.log 2>&1
cd "$ROOT/tool"
CARGO_BUILD_JOBS=2 cargo build --release --offline > "$ROOT/build.log" 2>&1
CARGO_BUILD_JOBS=2 cargo test --release --offline repaired_high_classical_tests > "$ROOT/wide-classical-tests.log" 2>&1
sha256sum target/release/value_prefilter > "$ROOT/binary-before.sha256"
cd "$ROOT"
timeout 2400 python3 run.py > validation-and-timing.log 2>&1
cd "$ROOT/tool"
sha256sum target/release/value_prefilter > "$ROOT/binary-after.sha256"
cmp "$ROOT/binary-before.sha256" "$ROOT/binary-after.sha256"
cd "$ROOT"
python3 - <<'PY'
from pathlib import Path
import hashlib,json
root=Path.cwd()
for name,expected in json.loads((root/'PREPARED_SOURCE.json').read_text()).items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name
(root/'SOURCE_UNCHANGED.json').write_text(json.dumps({'status':'ALL_PREPARED_TOOL_FILES_UNCHANGED','proof_accepted':False})+'\n')
PY
