#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ > observer.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; free -h; ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > observer-resume-preflight.log
cp -a ../precision-repair-20261016/observer-tip/target target-observer > observer-target-copy2.log 2>&1
code=$?;echo "$code" > observer-target-copy2.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-observer
cargo build --release --locked --offline --manifest-path observer/Cargo.toml --bin build_circuit > observer-build.log 2>&1
code=$?;echo "$code" > observer-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > observer.log 2>&1
code=$?;echo "$code" > observer.exit
exit "$code"
