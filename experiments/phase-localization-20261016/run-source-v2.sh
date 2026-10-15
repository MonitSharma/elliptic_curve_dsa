#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >source-v2.pid
while [ ! -f primitive-689514.exit ];do sleep 5;done
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight-source-v2.log
python3 prepare-source-v2.py >prepare-source-v2.log 2>&1
status=$?;echo $status >prepare-source-v2.exit;[ "$status" = 0 ] || exit "$status"
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/precision-repair-20261016/observer-tip/target
cp "$CARGO_TARGET_DIR/release/build_circuit" source-v1-build_circuit
cargo build --release --locked --offline --manifest-path source-observer-v2/Cargo.toml --bin build_circuit >build-source-v2.log 2>&1
status=$?;echo $status >build-source-v2.exit;[ "$status" = 0 ] || exit "$status"
"$CARGO_TARGET_DIR/release/build_circuit" >source-v2-map.log 2>&1
status=$?;echo $status >source-v2.exit;[ "$status" = 0 ] || exit "$status"
echo 'ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69  raw-builder.bin' | sha256sum -c - >source-v2-raw-verification.log 2>&1
status=$?;echo $status >source-v2-raw-verification.exit;exit "$status"
