#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > cache-v4.pid
trap 's=$?; echo "$s" > cache-v4.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > cache-v4-preflight.json
python3 prepare-cache-v4.py "$ROOT" > prepare-cache-v4.log
python3 prepare-counter-profile.py "$ROOT/candidate-control-fold-v4" "$BASE/base" "$ROOT/counter-control-fold-v4"
export CARGO_TARGET_DIR="$ROOT/cache-target-v4" F1_PROFILE=1
cargo +1.93.0 generate-lockfile --offline --manifest-path counter-control-fold-v4/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path counter-control-fold-v4/Cargo.toml > counter-control-fold-v4.log 2>&1
date -u
