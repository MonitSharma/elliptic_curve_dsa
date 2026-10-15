#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > generate-v3.pid
trap 's=$?; echo "$s" > generate-v3.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL FROGDROP_CK
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > generate-v3-preflight.json
python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/hclau/ecdsa_research/q692_readiness_20261015')
assert re.findall(r'test result: ok\. (\d+) passed; 0 failed',(p/'components-v3.log').read_text())[:5]==['7','5','2','1','2']
assert 'test result: ok. 16 passed; 0 failed' in (p/'phase-v3-proof.log').read_text()
assert 'DIFFERENTIAL_PASS cases=524288' in (p/'differential-v3-proof.log').read_text()
PY
python3 prepare-current-base-package.py "$ROOT/candidate-control-fold-v3" /home/hclau/ecdsa_research/overnight-20261014/product-leader441d-final-objectstore "$ROOT/package-control-fold-v3" "$ROOT/package-v3-evidence"
export CARGO_TARGET_DIR="$ROOT/package-target-v3"
cd package-control-fold-v3
/usr/bin/time -v cargo +1.93.0 build --release --locked --offline --bin build_circuit --bin eval_circuit > "$ROOT/package-v3-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" "$CARGO_TARGET_DIR/release/eval_circuit" > "$ROOT/package-v3-evidence/binaries.sha256"
mkdir "$ROOT/stream-v3-scratch"
cd "$ROOT/stream-v3-scratch"
export LOWQ_EXACT_STREAM_PATH="$ROOT/stream-v3.bin" F1_PROFILE=1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$ROOT/stream-v3-generation.log" 2>&1
sha256sum "$ROOT/stream-v3.bin" > "$ROOT/stream-v3.sha256"
date -u
