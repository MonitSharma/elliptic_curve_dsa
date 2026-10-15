#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/repair67-conditional-filter-20261016
cd "$ROOT"
echo $$ > run-v2.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run-v2.exit"' EXIT
test "$(cat run.exit)" = 127
test ! -e run-v2.exit
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight-v2.json
export PATH="/home/hclau/.cargo/bin:$PATH"
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 25165824
python3 - <<'PY'
from pathlib import Path
import hashlib,json
root=Path.cwd()
for name,h in json.loads((root/'PREPARED_SOURCE.json').read_text()).items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
PY
cd "$ROOT/tool"
CARGO_BUILD_JOBS=2 cargo build --release --offline > "$ROOT/build-v2.log" 2>&1
CARGO_BUILD_JOBS=2 cargo test --release --offline repaired_high_classical_tests > "$ROOT/wide-classical-tests-v2.log" 2>&1
sha256sum target/release/value_prefilter > "$ROOT/binary-before-v2.sha256"
cd "$ROOT"
timeout 2400 python3 run.py > validation-and-timing-v2.log 2>&1
cd "$ROOT/tool"
sha256sum target/release/value_prefilter > "$ROOT/binary-after-v2.sha256"
cmp "$ROOT/binary-before-v2.sha256" "$ROOT/binary-after-v2.sha256"
cd "$ROOT"
python3 - <<'PY'
from pathlib import Path
import hashlib,json
root=Path.cwd()
for name,h in json.loads((root/'PREPARED_SOURCE.json').read_text()).items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
(root/'SOURCE_UNCHANGED.json').write_text(json.dumps({'status':'ALL_PREPARED_TOOL_FILES_UNCHANGED','proof_accepted':False})+'\n')
PY
