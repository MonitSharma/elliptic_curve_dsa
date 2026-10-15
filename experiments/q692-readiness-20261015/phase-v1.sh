#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > phase-v1.pid
trap 's=$?; echo "$s" > phase-v1.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > phase-v1-preflight.json
python3 "$BASE/qubit-prepare-ht25-bankswap-v2-decision-proof.py" "$ROOT/candidate-control-fold-v1" "$BASE/base" "$ROOT/phase-control-fold-v1" "$BASE/evidence/ht25-bankswap-v2-decision/crate/phase-audit-kernel.rs" > phase-v1-source.json
export CARGO_TARGET_DIR="$ROOT/phase-target"
cargo +1.93.0 generate-lockfile --offline --manifest-path phase-control-fold-v1/Cargo.toml
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path phase-control-fold-v1/Cargo.toml coordinator_ -- --nocapture --test-threads=1 > phase-v1-proof.log 2>&1
date -u
