#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > "$ROOT/reflection-v7.pid"
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/reflection-v7.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > reflection-v7-preflight.json
python3 prepare-reflection-proof.py "$ROOT/candidate-control-fold-v7" "$BASE/base" "$ROOT/reflection-control-fold-v7" "$BASE/evidence/ht25-bankswap-v2-decision/crate/phase-audit-kernel.rs"
export CARGO_TARGET_DIR="$ROOT/reflection-target-v7"
cargo +1.93.0 generate-lockfile --offline --manifest-path reflection-control-fold-v7/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path reflection-control-fold-v7/Cargo.toml > reflection-v7-proof.log 2>&1
date -u
