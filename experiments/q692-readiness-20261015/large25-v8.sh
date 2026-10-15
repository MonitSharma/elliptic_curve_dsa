#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > large25-v8.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/large25-v8.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > large25-v8-preflight.json
python3 prepare-large25-proof.py "$ROOT/candidate-repair-v8" "$BASE/base" "$ROOT/large25-v8-crate" "$BASE/evidence/ht25-bankswap-v2-decision/crate/phase-audit-kernel.rs"
export CARGO_TARGET_DIR="$ROOT/large25-target-v8"
cargo +1.93.0 generate-lockfile --offline --manifest-path large25-v8-crate/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path large25-v8-crate/Cargo.toml > large25-v8-proof.log 2>&1
