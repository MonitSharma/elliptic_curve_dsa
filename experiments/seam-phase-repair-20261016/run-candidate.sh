#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/seam-phase-repair-20261016
echo $$ >candidate.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight-candidate.log
python3 prepare-candidate.py >prepare-candidate.log 2>&1
status=$?;echo $status >prepare-candidate.exit;[ "$status" = 0 ] || exit "$status"
rustc --edition=2021 --test -O guard-tests.rs -o guard-tests >build-guard-tests.log 2>&1
status=$?;echo $status >build-guard-tests.exit;[ "$status" = 0 ] || exit "$status"
./guard-tests --test-threads=1 >guard-tests.log 2>&1
status=$?;echo $status >guard-tests.exit;[ "$status" = 0 ] || exit "$status"
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/precision-repair-20261016/candidate-one-bit-top1/target
cp "$CARGO_TARGET_DIR/release/build_circuit" prior-familyA29-build_circuit
cargo build --release --locked --offline --manifest-path candidate/Cargo.toml --bin build_circuit >build-candidate.log 2>&1
status=$?;echo $status >build-candidate.exit;[ "$status" = 0 ] || exit "$status"
cd candidate
"$CARGO_TARGET_DIR/release/build_circuit" >../candidate.log 2>&1
status=$?;echo $status >../candidate.exit;[ "$status" = 0 ] || exit "$status"
sha256sum ops.bin ../prototype.bin >../candidate-stream.sha256
cmp ops.bin ../prototype.bin >../candidate-native-identity.log 2>&1
status=$?;echo $status >../candidate-native-identity.exit;exit "$status"
