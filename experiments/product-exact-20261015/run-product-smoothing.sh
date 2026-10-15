#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=product-smoothing-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
hostname > "$out/hostname.txt"
git -C ../toffoli status --short > "$out/repository-status.txt"
git -C ../toffoli branch --show-current > "$out/repository-branch.txt"
python3 prepare_product_smoothing.py > "$out/prepare.log" 2>&1
cd candidate-product-tail-smooth
cargo build --release --locked --offline --bin build_circuit > "../$out/build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "../$out/generate.log" 2>&1
sha256sum ops.bin > "../$out/stream.sha256"
cargo test --release --locked --offline --bin build_circuit point_add -- --test-threads=1 > "../$out/native-tests.log" 2>&1
cd "$root"
python3 stream_resources.py candidate-product-tail-smooth/ops.bin > "$out/resources.jsonl"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/census-preflight.json"
exe=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
"$exe" tip/ops.bin product-tail-smooth-20261016 0 4096 6 "$out/parent-census.jsonl" > "$out/parent-census.out" 2> "$out/parent-census.err" &
parent_pid=$!
echo "$parent_pid" > "$out/parent-census.pid"
"$exe" candidate-product-tail-smooth/ops.bin product-tail-smooth-20261016 0 4096 6 "$out/candidate-census.jsonl" > "$out/candidate-census.out" 2> "$out/candidate-census.err" &
candidate_pid=$!
echo "$candidate_pid" > "$out/candidate-census.pid"
wait "$parent_pid"
echo 0 > "$out/parent-census.exit"
wait "$candidate_pid"
echo 0 > "$out/candidate-census.exit"
