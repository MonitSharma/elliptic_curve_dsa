#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > product25-native.pid
trap 'rc=$?; echo "$rc" > "$root/product25-native.exit"' EXIT
while [ ! -f product-continuation-20261016/launcher.exit ]; do sleep 30; done
test "$(cat product-continuation-20261016/launcher.exit)" = 0
while [ ! -f extendedflags-native.exit ]; do sleep 30; done
test "$(cat extendedflags-native.exit)" = 0
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > product25-native-preflight.json
python3 prepare_product25_candidate.py > product25-native-prepare.log 2>&1
cd candidate-product-final25
cargo build --release --locked --offline --bin build_circuit > ../product25-native-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../product25-native-generate.log 2>&1
sha256sum ops.bin > ../product25-native.sha256
cmp ops.bin ../product-continuation-20261016/product-25-retained-1024.bin
cargo test --release --locked --offline --bin build_circuit exact_product_stage -- --test-threads=1 > ../product25-native-tests.log 2>&1
