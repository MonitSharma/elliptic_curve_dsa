#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > loan-markers.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-source
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >loan-markers-preflight.log
python3 prepare-loan-observer.py >loan-markers-prepare.log 2>&1
code=$?;echo "$code" >loan-markers-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --locked --offline --manifest-path source-loan-observer/Cargo.toml --bin build_circuit >loan-markers-build.log 2>&1
code=$?;echo "$code" >loan-markers-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >loan-markers.log 2>&1
code=$?;echo "$code" >loan-markers.exit
if [ "$code" -eq 0 ];then sha256sum raw-loan-builder.bin >raw-loan-builder.sha256;fi
exit "$code"
