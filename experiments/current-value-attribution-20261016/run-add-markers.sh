#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > add-markers.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-source
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >add-markers-preflight.log
python3 prepare-add-observer.py >add-markers-prepare.log 2>&1
code=$?;echo "$code" >add-markers-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --locked --offline --manifest-path source-add-observer/Cargo.toml --bin build_circuit >add-markers-build.log 2>&1
code=$?;echo "$code" >add-markers-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >add-markers.log 2>&1
code=$?;echo "$code" >add-markers.exit
if [ "$code" -eq 0 ];then sha256sum raw-add-builder.bin >raw-add-builder.sha256;fi
exit "$code"
