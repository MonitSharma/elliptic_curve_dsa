#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > final.pid
trap 'rc=$?; echo "$rc" > "$root/final.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > final-preflight.json
python3 prepare_final.py > final-prepare.log 2>&1
cd candidate-final
cargo build --release --locked --offline --bin build_circuit > ../final-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../final-generate.log 2>&1
sha256sum ops.bin > ../final.sha256
cmp ops.bin ../chain-retained.bin
cargo test --release --locked --offline --bin build_circuit exact_product_stage -- --test-threads=1 > ../final-native-tests.log 2>&1
