#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide67-native-20261016
cd "$root"
echo $$ > run.pid
trap 'echo $? > /home/hclau/ecdsa_research/wide67-native-20261016/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 33554432
python3 prepare.py > prepare.log 2>&1
cd wide67/candidate
cargo test --release --locked --offline --bin build_circuit frozen_cache_wide67::tests -- --test-threads=1 > ../native-tests.log 2>&1
cargo build --release --locked --offline --bin build_circuit > ../build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../generate.log 2>&1
cd "$root"
python3 /home/hclau/ecdsa_research/server-preflight.py > census-preflight.json
python3 census.py wide67 > census.log 2>&1
