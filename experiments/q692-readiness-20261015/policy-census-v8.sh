#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
cd "$ROOT"
echo "$$" > "$ROOT/policy-census-v8.pid"
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/policy-census-v8.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > policy-census-v8-preflight.json
python3 prepare-policy-census.py "$ROOT"
export CARGO_TARGET_DIR="$ROOT/policy-census-target-v8"
cargo +1.93.0 generate-lockfile --offline --manifest-path policy-census-v8/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path policy-census-v8/Cargo.toml -- "$ROOT/failed-v6-packet-r2.json" "$ROOT/policy-census-v8.json" > policy-census-v8-diagnostics.log 2>&1
date -u
