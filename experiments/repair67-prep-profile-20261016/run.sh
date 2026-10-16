#!/bin/bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/repair67-prep-profile-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'echo $? > "$ROOT/run.exit"' EXIT
export PATH="/home/hclau/.cargo/bin:$PATH" CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
python3 prepare.py > prepare.log 2>&1
cd tool
cargo build --release --locked --offline > ../build.log 2>&1
sha256sum target/release/value_prefilter > ../binary-before.sha256
cd "$ROOT"
timeout 1200 python3 run.py > profile.log 2>&1
cd tool
sha256sum target/release/value_prefilter > ../binary-after.sha256
cd "$ROOT"
cmp binary-before.sha256 binary-after.sha256
python3 - <<'PY'
from pathlib import Path
import hashlib,json
r=Path.cwd()
for name,h in json.loads((r/'PREPARED_SOURCE.json').read_text()).items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==h,name
(r/'SOURCE_UNCHANGED.json').write_text(json.dumps({'status':'ALL_INSTRUMENTED_SOURCES_UNCHANGED','proof_accepted':False})+'\n')
PY
