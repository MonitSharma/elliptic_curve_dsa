#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/n2-loan-retention-20261016
echo $$ > all-retained.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-source
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18;git -C ../product-exact-20261015/tip branch --show-current;git -C ../product-exact-20261015/tip status --short; } >all-retained-preflight.log
python3 prepare-n2-retention.py >all-retained-prepare.log 2>&1
code=$?;echo "$code" >all-retained-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --locked --offline --manifest-path all-retained/Cargo.toml --bin build_circuit >all-retained-build.log 2>&1
code=$?;echo "$code" >all-retained-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd all-retained
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >../all-retained-generation.log 2>&1
code=$?;echo "$code" >../all-retained-generation.exit
exit "$code"
