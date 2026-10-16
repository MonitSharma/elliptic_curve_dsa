#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-exact-20261015
d=$r/all70-native67-20261016
cd "$r"
mkdir -p "$d"
echo $$ > "$d/launcher.pid"
trap 'echo $? > "$d/launcher.exit"' EXIT
while [ ! -f "$r/all70-cache67-20261016/cache-launcher.exit" ]; do sleep 10; done
test "$(cat "$r/all70-cache67-20261016/cache-launcher.exit")" = 0
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 25165824
while ! python3 "$r/all70_resource_guard.py" 2 "$d/prepare-resource-admission.jsonl"; do sleep 30; done
python3 /home/hclau/ecdsa_research/server-preflight.py > "$d/prepare-preflight.json"
python3 "$r/prepare_all70_native67.py" > "$d/prepare.log" 2>&1
cd "$d/candidate"
while ! python3 "$r/all70_resource_guard.py" 2 "$d/build-resource-admission.jsonl"; do sleep 30; done
cargo test --release --locked --offline --bin build_circuit frozen_cache_all70_67 -- --test-threads=1 > "$d/loader-tests.log" 2>&1
cargo test --release --locked --offline --bin build_circuit all70_uniform_tests -- --test-threads=1 > "$d/family-tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$d/build.log" 2>&1
while ! python3 "$r/all70_resource_guard.py" 1 "$d/generate-resource-admission.jsonl"; do sleep 30; done
/usr/bin/time -v taskset -c 126 target/release/build_circuit > "$d/generate.log" 2>&1
python3 "$r/verify_all70_native67.py" > "$d/native-verification.log" 2>&1
