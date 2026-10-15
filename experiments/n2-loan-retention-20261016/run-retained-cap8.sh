#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/n2-loan-retention-20261016
echo $$ > all-retained-cap8.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-source
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >all-retained-cap8-preflight.log
python3 prepare-retained-cap8.py >all-retained-cap8-prepare.log 2>&1
code=$?;echo "$code" >all-retained-cap8-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --locked --offline --manifest-path all-retained-cap8/Cargo.toml --bin build_circuit >all-retained-cap8-build.log 2>&1
code=$?;echo "$code" >all-retained-cap8-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd all-retained-cap8
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >../all-retained-cap8-generation.log 2>&1
code=$?;echo "$code" >../all-retained-cap8-generation.exit
exit "$code"
