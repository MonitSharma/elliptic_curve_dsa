#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-carry-readers-20261019
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-carry-readers-20261019/gaps.exit' EXIT
python3 preflight.py > gaps-preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RUSTUP_TOOLCHAIN=stable CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo build --release --offline --bin carry_inspect_gaps > gaps-build.log 2>&1
"$CARGO_TARGET_DIR/release/carry_inspect_gaps" /home/hclau/ecdsa_research/product-carry-readers-20261019
