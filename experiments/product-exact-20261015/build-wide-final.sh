#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > wide-final.pid
trap 'rc=$?; echo "$rc" > "$root/wide-final.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > wide-final-preflight.json
python3 prepare_wide_final.py > wide-final-prepare.log 2>&1
cd wide-candidate-final
cargo build --release --locked --offline --bin build_circuit > ../wide-final-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../wide-final-generate.log 2>&1
sha256sum ops.bin > ../wide-final.sha256
cmp ops.bin ../wide-chain-retained.bin
cargo test --release --locked --offline --bin build_circuit exact_product_stage -- --test-threads=1 > ../wide-final-native-tests.log 2>&1
