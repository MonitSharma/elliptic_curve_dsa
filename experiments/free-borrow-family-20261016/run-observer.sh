#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/free-borrow-family-20261016
echo $$ >observer.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight.log
python3 prepare-observer.py >prepare-observer.log 2>&1
status=$?;echo $status >prepare-observer.exit;[ "$status" = 0 ] || exit "$status"
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/precision-repair-20261016/observer-tip/target
cp "$CARGO_TARGET_DIR/release/build_circuit" preserved-source-v2-build_circuit
cargo build --release --locked --offline --manifest-path observer/Cargo.toml --bin build_circuit >build-observer.log 2>&1
status=$?;echo $status >build-observer.exit;[ "$status" = 0 ] || exit "$status"
"$CARGO_TARGET_DIR/release/build_circuit" >source-map.log 2>&1
status=$?;echo $status >observer.exit;[ "$status" = 0 ] || exit "$status"
echo 'ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69  raw-builder.bin' | sha256sum -c - >raw-verification.log 2>&1
status=$?;echo $status >raw-verification.exit;exit "$status"
