#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > differential-v2.pid
trap 's=$?; echo "$s" > differential-v2.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > differential-v2-preflight.json
python3 prepare-differential.py "$BASE/candidate-ht25-bankswap-v2" "$ROOT/candidate-control-fold-v2" "$BASE/base" "$ROOT/differential-control-fold-v2"
export CARGO_TARGET_DIR="$ROOT/differential-target-v2"
cargo +1.93.0 generate-lockfile --offline --manifest-path differential-control-fold-v2/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path differential-control-fold-v2/Cargo.toml > differential-v2-proof.log 2>&1
date -u
