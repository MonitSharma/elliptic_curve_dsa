#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=repair67-native-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 20971520
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/prepare-preflight.json"
python3 prepare_repair67_native.py > "$out/prepare.log" 2>&1
cd "$root/$out/candidate"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/$out/build-preflight.json"
cargo test --release --locked --offline --bin build_circuit frozen_cache_repair67 -- --test-threads=1 > "$root/$out/loader-native-tests.log" 2>&1
cargo test --release --locked --offline --bin build_circuit precision_family::tests -- --test-threads=1 > "$root/$out/precision-native-tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$root/$out/build.log" 2>&1
task_cpu=$(python3 -c 'import os; print(max(os.sched_getaffinity(0)))')
/usr/bin/time -v taskset -c "$task_cpu" ./target/release/build_circuit > "$root/$out/generate.log" 2>&1
cd "$root"
python3 qualify_repair67_native.py --native-only > "$out/qualification.log" 2>&1
