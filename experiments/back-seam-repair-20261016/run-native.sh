#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/back-seam-repair-20261016
echo $$ >native.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; pgrep -af 'cargo build|rustc' || true; } >preflight-native.log
python3 prepare-native.py >prepare-native.log 2>&1
status=$?;echo "$status" >prepare-native.exit;[ "$status" = 0 ] || exit "$status"
rustc --edition=2021 --test -O -Ccodegen-units=1 guard-tests.rs -o guard-tests >build-guard-tests.log 2>&1
status=$?;echo "$status" >build-guard-tests.exit;[ "$status" = 0 ] || exit "$status"
./guard-tests --test-threads=1 >guard-tests.log 2>&1
status=$?;echo "$status" >guard-tests.exit;[ "$status" = 0 ] || exit "$status"
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/precision-repair-20261016/candidate-one-bit-top1/target
cp "$CARGO_TARGET_DIR/release/build_circuit" preserved-front-seam-build_circuit
cargo build --release --locked --offline --manifest-path candidate/Cargo.toml --bin build_circuit >build-native.log 2>&1
status=$?;echo "$status" >build-native.exit;[ "$status" = 0 ] || exit "$status"
cd candidate
"$CARGO_TARGET_DIR/release/build_circuit" >../native.log 2>&1
status=$?;echo "$status" >../native.exit;[ "$status" = 0 ] || exit "$status"
cd ..
python3 verify-native.py >native-verification.log 2>&1
status=$?;echo "$status" >native-verification.exit;exit "$status"
