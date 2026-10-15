#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > primitive-v3.pid
trap 's=$?; echo "$s" > primitive-v3.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > primitive-v3-preflight.json
python3 prepare-primitive-proof.py "$ROOT/candidate-control-fold-v3" "$BASE/base" "$ROOT/primitive-control-fold-v3"
export CARGO_TARGET_DIR="$ROOT/primitive-target-v3"
cargo +1.93.0 generate-lockfile --offline --manifest-path primitive-control-fold-v3/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path primitive-control-fold-v3/Cargo.toml > primitive-v3-proof.log 2>&1
date -u
