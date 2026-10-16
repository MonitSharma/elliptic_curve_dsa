#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > seed-markers.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-source
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >seed-markers-preflight.log
python3 prepare-seed-observer.py >seed-markers-prepare.log 2>&1
code=$?;echo "$code" >seed-markers-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --locked --offline --manifest-path source-seed-observer/Cargo.toml --bin build_circuit >seed-markers-build.log 2>&1
code=$?;echo "$code" >seed-markers-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >seed-markers.log 2>&1
code=$?;echo "$code" >seed-markers.exit
if [ "$code" -eq 0 ];then sha256sum raw-seed-builder.bin >raw-seed-builder.sha256;fi
exit "$code"
