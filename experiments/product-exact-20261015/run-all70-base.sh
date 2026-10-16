#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-exact-20261015
d=$r/all70-cache67-20261016
mkdir -p "$d"
echo $$ > "$d/base-launcher.pid"
trap 'echo $? > "$d/base-launcher.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > "$d/base-preflight.json"
python3 "$r/prepare_all70_base.py" > "$d/base-prepare.log" 2>&1
cd "$r/candidate-all70-base"
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
cargo test --release --locked --offline --bin build_circuit all70_uniform_tests > "$d/base-tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$d/base-build.log" 2>&1
/usr/bin/time -v target/release/build_circuit > "$d/base-generate.log" 2>&1
sha256sum ops.bin > "$d/base-stream.sha256"
python3 "$r/verify_all70_base.py" > "$d/base-verification.log" 2>&1
