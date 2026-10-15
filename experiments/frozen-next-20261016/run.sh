#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/frozen-next-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/frozen-next-20261016/run.exit' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 33554432
for name in product53 wide43; do
 python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
 python3 prepare.py "$name" > "$name-prepare.log" 2>&1
 cd "$root/$name/candidate"
 cargo test --release --locked --offline --bin build_circuit "frozen_cache_$name::tests" -- --test-threads=1 > "$root/$name/native-tests.log" 2>&1
 cargo build --release --locked --offline --bin build_circuit > "$root/$name/build.log" 2>&1
 /usr/bin/time -v ./target/release/build_circuit > "$root/$name/generate.log" 2>&1
 cd "$root"
 python3 census.py "$name" > "$name-census.log" 2>&1
done
