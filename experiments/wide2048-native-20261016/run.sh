#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/wide2048-native-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 25165824
python3 prepare.py > prepare.log 2>&1
cd wide2048/candidate
cargo test --release --locked --offline --bin build_circuit frozen_cache_wide2048::tests -- --test-threads=1 > ../native-tests.log 2>&1
cargo build --release --locked --offline --bin build_circuit > ../build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../generate.log 2>&1
cd "$ROOT"
python3 /home/hclau/ecdsa_research/server-preflight.py > census-preflight.json
python3 census.py > census.log 2>&1
