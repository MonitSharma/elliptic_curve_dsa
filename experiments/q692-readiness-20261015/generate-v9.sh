#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
cd "$ROOT"
echo "$$" > "$ROOT/generate-v9.pid"
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/generate-v9.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL FROGDROP_CK
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > "$ROOT/generate-v9-preflight.json"
python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/hclau/ecdsa_research/q692_readiness_20261015')
assert re.findall(r'test result: ok\. (\d+) passed; 0 failed',(p/'components-v9.log').read_text())[:5]==['7','5','2','1','2']
assert 'test result: ok. 16 passed; 0 failed' in (p/'phase-v9-proof.log').read_text()
assert 'FIXED_COLUMN_SUITE_PASS cases=1024' in (p/'fixed-column-v9-r5-proof.log').read_text()
assert 'LARGE25_PASS cases=131072' in (p/'large25-v8-proof.log').read_text()
PY
python3 prepare-current-base-package.py "$ROOT/candidate-repair-v9" /home/hclau/ecdsa_research/overnight-20261014/product-leader441d-final-objectstore "$ROOT/package-control-fold-v9" "$ROOT/package-v9-evidence"
export CARGO_TARGET_DIR="$ROOT/package-target-v9"
cd "$ROOT/package-control-fold-v9"
/usr/bin/time -v cargo +1.93.0 build --release --locked --offline --bin build_circuit --bin eval_circuit > "$ROOT/package-v9-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" "$CARGO_TARGET_DIR/release/eval_circuit" > "$ROOT/package-v9-evidence/binaries.sha256"
mkdir "$ROOT/stream-v9-scratch"
cd "$ROOT/stream-v9-scratch"
export LOWQ_EXACT_STREAM_PATH="$ROOT/stream-v9.bin" F1_PROFILE=1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$ROOT/stream-v9-generation.log" 2>&1
sha256sum "$ROOT/stream-v9.bin" > "$ROOT/stream-v9.sha256"
date -u
