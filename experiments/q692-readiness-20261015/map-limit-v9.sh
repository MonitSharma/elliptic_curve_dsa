#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > map-limit-v9.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/map-limit-v9.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > map-limit-v9-preflight.json
python3 prepare-map-limit-proof.py "$ROOT/candidate-repair-v9" "$BASE/base" "$ROOT/map-limit-v9-crate" "$BASE/evidence/ht25-bankswap-v2-decision/crate/phase-audit-kernel.rs"
export CARGO_TARGET_DIR="$ROOT/map-limit-target-v9"
cargo +1.93.0 generate-lockfile --offline --manifest-path map-limit-v9-crate/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path map-limit-v9-crate/Cargo.toml > map-limit-v9-proof.log 2>&1
