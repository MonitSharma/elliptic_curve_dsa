#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-exact-20261015
d=$r/all70-cache67-20261016
mkdir "$d/initial-cargo-path-failure"
cp "$r/run-all70-base.sh" "$d/base-launcher.pid" "$d/base-launcher.exit" "$d/base-tests.log" "$d/initial-cargo-path-failure/"
echo $$ > "$d/base-launcher.pid"
rm "$d/base-launcher.exit"
trap 'echo $? > "$d/base-launcher.exit"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > "$d/base-build-preflight.json"
cd "$r/candidate-all70-base"
cargo test --release --locked --offline --bin build_circuit all70_uniform_tests -- --test-threads=1 > "$d/base-tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$d/base-build.log" 2>&1
/usr/bin/time -v taskset -c 126 target/release/build_circuit > "$d/base-generate.log" 2>&1
sha256sum ops.bin > "$d/base-stream.sha256"
python3 "$r/verify_all70_base.py" > "$d/base-verification.log" 2>&1
