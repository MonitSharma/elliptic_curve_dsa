#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/seed-restore-20261016
echo $$ >native.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18;git -C candidate rev-parse HEAD;git -C candidate status --short; } >native-preflight.log
python3 ../current-value-attribution-20261016/prepare-seed-protected.py >protected-prepare.log 2>&1
code=$?;echo "$code" >protected-prepare.exit;if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
cargo test --release --locked --offline --manifest-path tool/Cargo.toml --bin native_guard -- --test-threads=1 >guard-tests.log 2>&1
code=$?;echo "$code" >guard-tests.exit;if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --locked --offline --manifest-path tool/Cargo.toml --bin protected_seed >protected-build.log 2>&1
code=$?;echo "$code" >protected-build.exit;if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/protected_seed" >protected.log 2>&1
code=$?;echo "$code" >protected.exit;if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-source
cp "$CARGO_TARGET_DIR/release/build_circuit" preserved-seed-observer-build_circuit
cargo build --release --locked --offline --manifest-path candidate/Cargo.toml --bin build_circuit >native-build.log 2>&1
code=$?;echo "$code" >native-build.exit;if [ "$code" -ne 0 ];then exit "$code";fi
cd candidate
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >../native.log 2>&1
code=$?;echo "$code" >../native.exit;exit "$code"
