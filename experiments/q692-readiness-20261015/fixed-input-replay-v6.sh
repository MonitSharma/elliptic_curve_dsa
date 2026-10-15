#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > "$ROOT/fixed-input-replay-v6.pid"
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/fixed-input-replay-v6.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > fixed-input-replay-v6-preflight.json
python3 prepare-fixed-input-replay.py "$BASE/base" "$ROOT/fixed-input-replay-v6-crate"
export CARGO_TARGET_DIR="$ROOT/fixed-input-target-v6"
cargo +1.93.0 generate-lockfile --offline --manifest-path fixed-input-replay-v6-crate/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path fixed-input-replay-v6-crate/Cargo.toml -- "$BASE/evidence/ht25-bankswap-v2-ops.bin" "$ROOT/failed-v6-packet-r2.json" "$ROOT/fixed-input-original-vs-v6.json" > fixed-input-original-replay.log 2>&1
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path fixed-input-replay-v6-crate/Cargo.toml -- "$ROOT/clean-replay-v6-binary/ops.bin" "$ROOT/failed-v6-packet-r2.json" "$ROOT/fixed-input-v6-replay.json" > fixed-input-v6-replay.log 2>&1
date -u
