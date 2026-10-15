#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/back-seam-repair-20261016
echo $$ >zero-tool.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/seam-phase-repair-20261016/tool/target
python3 prepare-zero-tool.py >prepare-zero-tool.log 2>&1
status=$?;echo "$status" >prepare-zero-tool.exit;[ "$status" = 0 ] || exit "$status"
cargo build --release --offline --manifest-path tool/Cargo.toml --bin zero_prefix >build-zero-tool.log 2>&1
status=$?;echo "$status" >build-zero-tool.exit;[ "$status" = 0 ] || exit "$status"
"$CARGO_TARGET_DIR/release/zero_prefix" ../product-exact-20261015/tip/ops.bin prefix-zero-receipt.json >prefix-exact-zero-receipt.json 2>prefix-exact-zero.log
status=$?;echo "$status" >prefix-exact-zero.exit;exit "$status"
