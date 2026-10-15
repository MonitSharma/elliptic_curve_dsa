#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ > support.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; free -h; ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >support-preflight.log
python3 prepare-support.py >support-prepare.log 2>&1
code=$?;echo "$code" >support-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-tool
cargo build --release --locked --offline --manifest-path tool/Cargo.toml --bin support_donors >support-build.log 2>&1
code=$?;echo "$code" >support-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/support_donors" ../product-exact-20261015/tip/ops.bin terminal-queries.txt >support-zeros.jsonl 2>support-run.log
code=$?;echo "$code" >support.exit
exit "$code"
