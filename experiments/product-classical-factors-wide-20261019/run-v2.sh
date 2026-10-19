#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-factors-wide-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-factors-wide-20261019/run-v2.exit' EXIT
test "$(cat run.exit)" = 101
python3 ../autonomous-20261019/preflight_v9.py > preflight-v2.json
sha256sum *.py *.rs proof/*.rs Cargo.toml run-v2.sh ../autonomous-20261019/preflight_v9.py > SOURCE_V2.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTUP_TOOLCHAIN=stable CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin classical_factors_wide -- --test-threads=1 > tests-v2.log 2>&1
cargo build --release --offline --bins > build-v2.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/classical_factors_wide" "$CARGO_TARGET_DIR/release/classical_factors_wide_trace" > BINARY_V2.sha256
CLASSICAL_WIDE_CAP=7 /usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_factors_wide" ../product-pareto-20261019/candidate-parent4/ops.bin "$r/compat7" 97c40ed1dd3f5123c9554ebf29c54c433960804c0effce63dc7bba52844ae9ae > compat7.log 2>&1
python3 -c 'import json; assert json.load(open("compat7.json"))["output_full_sha3_256"]=="f64a9d8c59cdc89e9b683988da84eb34fa78c5a884f0324ce824e4c07a00fa53"'
CLASSICAL_WIDE_CAP=9 /usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_factors_wide" ../product-classical-nine-20261019/candidate/ops.bin "$r/wide9" 4b81cbc1e247e791ab11ff56c5f84b4da5edc8618d7c19fe590305390fa6f93f > wide9.log 2>&1
if [ -f wide9.ops.bin ]; then
 /usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_factors_wide_trace" ../product-classical-nine-20261019/candidate/ops.bin wide9.ops.bin CONTROL.json > control.log 2>&1
fi
