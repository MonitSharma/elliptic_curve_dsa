#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > wide-compound-native.pid
trap 'rc=$?; echo "$rc" > "$root/wide-compound-native.exit"' EXIT
while [ ! -f extendedflags-native.exit ]; do sleep 30; done
test "$(cat extendedflags-native.exit)" = 0
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > wide-compound-native-preflight.json
python3 prepare_wide_compound_candidate.py > wide-compound-native-prepare.log 2>&1
cd candidate-wide-compound
cargo build --release --locked --offline --bin build_circuit > ../wide-compound-native-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../wide-compound-native-generate.log 2>&1
sha256sum ops.bin > ../wide-compound-native.sha256
cmp ops.bin ../wide-compound-20261016/wide-15-retained-512.bin
cargo test --release --locked --offline --bin build_circuit exact_wide_stage -- --test-threads=1 > ../wide-compound-native-tests.log 2>&1
cd "$root"
out=wide-compound-frozen-20261016
mkdir -p "$out"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
exe=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
"$exe" /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin wide-compound-frozen-20261016 0 4096 6 "$out/parent-census.jsonl" > "$out/parent-census.out" 2> "$out/parent-census.err" &
parent_pid=$!;echo "$parent_pid" > "$out/parent-census.pid"
"$exe" candidate-wide-compound/ops.bin wide-compound-frozen-20261016 0 4096 6 "$out/candidate-census.jsonl" > "$out/candidate-census.out" 2> "$out/candidate-census.err" &
candidate_pid=$!;echo "$candidate_pid" > "$out/candidate-census.pid"
wait "$parent_pid";echo 0 > "$out/parent-census.exit"
wait "$candidate_pid";echo 0 > "$out/candidate-census.exit"
