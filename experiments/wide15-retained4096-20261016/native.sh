#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/wide15-retained4096-20261016
echo $$ > native-launcher.pid
trap 'rc=$?; echo "$rc" > native-launcher.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > native-preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 25165824
python3 prepare_native.py > native-prepare.log 2>&1
cd candidate
cargo test --release --locked --offline --bin build_circuit frozen_retained4096::tests -- --test-threads=1 > ../native-tests.log 2>&1
cargo build --release --locked --offline --bin build_circuit > ../native-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../native-generate.log 2>&1
cd ..
python3 verify_native.py > native-verify.log 2>&1
