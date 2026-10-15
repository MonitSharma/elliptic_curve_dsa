#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
cd "$ROOT"
echo "$$" > independent-policy-v9.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/independent-policy-v9.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > independent-policy-v9-preflight.json
python3 prepare-independent-policy.py "$ROOT"
export CARGO_TARGET_DIR="$ROOT/independent-policy-target-v9"
cargo +1.93.0 generate-lockfile --offline --manifest-path independent-policy-v9/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path independent-policy-v9/Cargo.toml -- "$ROOT/independent-policy-v9.json" > independent-policy-v9-proof.log 2>&1
