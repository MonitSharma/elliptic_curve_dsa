#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > fixed-column-v9-r2.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/fixed-column-v9-r2.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > fixed-column-v9-r2-preflight.json
python3 prepare-fixed-column-proof.py "$ROOT/candidate-repair-v9" "$BASE/base" "$ROOT/fixed-column-v9-r2-crate" "$BASE/evidence/ht25-bankswap-v2-decision/crate/phase-audit-kernel.rs"
export CARGO_TARGET_DIR="$ROOT/fixed-column-target-v9"
cargo +1.93.0 generate-lockfile --offline --manifest-path fixed-column-v9-r2-crate/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path fixed-column-v9-r2-crate/Cargo.toml > fixed-column-v9-r2-proof.log 2>&1
