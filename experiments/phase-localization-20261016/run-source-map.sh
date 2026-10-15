#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >source-map.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 prepare-source-map.py >prepare-source-map.log 2>&1
status=$?;echo $status >prepare-source-map.exit;[ "$status" = 0 ] || exit "$status"
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/precision-repair-20261016/observer-tip/target
cp "$CARGO_TARGET_DIR/release/build_circuit" prior-isolated-build_circuit
cargo build --release --locked --offline --manifest-path source-observer/Cargo.toml --bin build_circuit >build-source-map.log 2>&1
status=$?;echo $status >build-source-map.exit;[ "$status" = 0 ] || exit "$status"
"$CARGO_TARGET_DIR/release/build_circuit" >source-map.log 2>&1
status=$?;echo $status >source-map.exit
exit "$status"
