#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/seam-phase-repair-20261016
echo $$ >proofs.pid
while [ ! -f candidate.exit ];do sleep 5;done
[ "$(cat candidate.exit)" = 0 ] || exit 1
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight-proofs.log
python3 verify-native.py >native-verification.log 2>&1
status=$?;echo $status >native-verification.exit;[ "$status" = 0 ] || exit "$status"
python3 prepare-proofs.py >prepare-proofs.log 2>&1
status=$?;echo $status >prepare-proofs.exit;[ "$status" = 0 ] || exit "$status"
cargo test --release --manifest-path tool/Cargo.toml --bin phase_primitive -- --test-threads=1 >proof-algebra-tests.log 2>&1
status=$?;echo $status >proof-algebra-tests.exit;[ "$status" = 0 ] || exit "$status"
cargo build --release --manifest-path tool/Cargo.toml --bin phase_primitive >build-proofs.log 2>&1
status=$?;echo $status >build-proofs.exit;[ "$status" = 0 ] || exit "$status"
tool/target/release/phase_primitive old-component.bin 0 >old-phase-contract.json 2>old-phase-contract.log
status=$?;echo $status >old-phase-contract.exit;[ "$status" = 0 ] || exit "$status"
tool/target/release/phase_primitive new-component.bin 0 >new-phase-contract.json 2>new-phase-contract.log
status=$?;echo $status >new-phase-contract.exit;[ "$status" = 0 ] || exit "$status"
tool/target/release/phase_primitive negative-wrong-clifford.bin 0 >negative-phase-contract.json 2>negative-phase-contract.log
status=$?;echo $status >negative-phase-contract.exit;[ "$status" != 0 ] || exit 1
python3 verify-proof-results.py >verify-proof-results.log 2>&1
status=$?;echo $status >verify-proof-results.exit;[ "$status" = 0 ] || exit "$status"
echo 0 >proofs.exit
