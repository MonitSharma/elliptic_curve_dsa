#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > extendedflags-native.pid
trap 'rc=$?; echo "$rc" > "$root/extendedflags-native.exit"' EXIT
while [ ! -f flags-extended-20261016/launcher.exit ]; do sleep 30; done
test "$(cat flags-extended-20261016/launcher.exit)" = 0
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > extendedflags-native-preflight.json
python3 prepare_flags_candidate.py > extendedflags-native-prepare.log 2>&1
cd candidate-product-extendedflags
cargo build --release --locked --offline --bin build_circuit > ../extendedflags-native-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../extendedflags-native-generate.log 2>&1
sha256sum ops.bin > ../extendedflags-native.sha256
cmp ops.bin ../flags-extended-20261016/product-11-retained-1024.bin
cargo test --release --locked --offline --bin build_circuit exact_product_stage -- --test-threads=1 > ../extendedflags-native-tests.log 2>&1
