#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ >square-native.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -20;git -C ../product-exact-20261015/tip rev-parse HEAD;git -C ../product-exact-20261015/tip status --short; } >square-native-preflight.log
python3 freeze-square-family.py >square-family-freeze.log 2>&1
code=$?;echo "$code" >square-family-freeze.exit
if [ "$code" -ne 0 ];then exit "$code";fi
python3 prepare-square-candidate.py >square-candidate-prepare.log 2>&1
code=$?;echo "$code" >square-candidate-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-tool
cargo test --release --locked --offline --manifest-path tool/Cargo.toml --bin square_native_guard -- --test-threads=1 >square-guard-tests.log 2>&1
code=$?;echo "$code" >square-guard-tests.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-observer
cp "$CARGO_TARGET_DIR/release/build_circuit" preserved-square-component-build_circuit
cargo build --release --locked --offline --manifest-path square4-candidate/Cargo.toml --bin build_circuit >square-native-build.log 2>&1
code=$?;echo "$code" >square-native-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd square4-candidate
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >../square-native.log 2>&1
code=$?;echo "$code" >../square-native.exit
exit "$code"
