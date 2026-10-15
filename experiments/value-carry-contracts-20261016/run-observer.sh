#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; git -C ../product-exact-20261015/tip rev-parse HEAD; git -C ../product-exact-20261015/tip status --short; } > observer-preflight.log
python3 prepare-observer.py > observer-prepare.log 2>&1
code=$?;echo "$code" > observer-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cp -a ../quantum-borrow-family-20261016/frame-observer/target target-observer > observer-target-copy.log 2>&1
code=$?;echo "$code" > observer-target-copy.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd observer
# A private target path; dependencies may be hardlinked/copied later without
# changing any existing frozen build products.
export CARGO_TARGET_DIR=../target-observer
cargo build --release --locked --offline --bin build_circuit > ../observer-build.log 2>&1
code=$?;echo "$code" > ../observer-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > ../observer.log 2>&1
code=$?;echo "$code" > ../observer.exit
exit "$code"
