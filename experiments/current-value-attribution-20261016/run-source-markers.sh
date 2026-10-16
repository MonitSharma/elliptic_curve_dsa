#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > source-markers.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } >source-markers-preflight.log
python3 prepare-attribution.py >source-markers-prepare.log 2>&1
code=$?;echo "$code" >source-markers-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cp -a ../value-carry-contracts-20261016/target-observer target-source >target-copy.log 2>&1
code=$?;echo "$code" >target-copy.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-source
cargo build --release --locked --offline --manifest-path source-observer/Cargo.toml --bin build_circuit >source-markers-build.log 2>&1
code=$?;echo "$code" >source-markers-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >source-markers.log 2>&1
code=$?;echo "$code" >source-markers.exit
if [ "$code" -eq 0 ];then sha256sum raw-builder.bin >raw-builder.sha256;fi
exit "$code"
