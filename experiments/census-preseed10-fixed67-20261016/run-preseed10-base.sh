#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/census-preseed10-fixed67-20261016
d=$r/preseed10-cache67-20261016
mkdir -p "$d"
echo $$ > "$d/base-launcher.pid"
trap 'echo $? > "$d/base-launcher.exit"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > "$d/base-preflight.json"
python3 "$r/prepare_preseed10_base.py" > "$d/base-prepare.log" 2>&1
cd "$r/candidate-preseed10-base"
cargo test --release --locked --offline --bin build_circuit preseed10_uniform_tests -- --test-threads=1 > "$d/base-tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$d/base-build.log" 2>&1
/usr/bin/time -v target/release/build_circuit > "$d/base-generate.log" 2>&1
sha256sum ops.bin > "$d/base-stream.sha256"
python3 "$r/verify_preseed10_base.py" > "$d/base-verification.log" 2>&1
