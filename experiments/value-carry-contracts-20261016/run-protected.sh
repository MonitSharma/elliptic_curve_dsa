#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ > protected.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; free -h; ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > protected-preflight.log
python3 prepare-protected.py > protected-prepare.log 2>&1
code=$?;echo "$code" > protected-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cp -a ../seam-phase-repair-20261016/tool/target target-tool > protected-copy.log 2>&1
code=$?;echo "$code" > protected-copy.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-tool
cargo build --release --offline --locked --manifest-path tool/Cargo.toml --bin protected_terminal > protected-build.log 2>&1
code=$?;echo "$code" > protected-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
"$CARGO_TARGET_DIR/release/protected_terminal" > protected.json 2> protected.log
code=$?;echo "$code" > protected.exit
exit "$code"
