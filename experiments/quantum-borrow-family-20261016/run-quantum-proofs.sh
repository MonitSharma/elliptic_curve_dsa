#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/quantum-borrow-family-20261016
echo $$ >quantum-proofs.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/seam-phase-repair-20261016/tool/target
python3 prepare-quantum-proof.py >prepare-quantum-proof.log 2>&1
status=$?; echo $status >prepare-quantum-proof.exit; [ "$status" = 0 ] || exit "$status"
cargo test --release --offline --manifest-path proof-tool/Cargo.toml --bin quantum_phase -- --test-threads=1 >quantum-algebra-tests.log 2>&1
status=$?; echo $status >quantum-algebra-tests.exit; [ "$status" = 0 ] || exit "$status"
cargo build --release --offline --manifest-path proof-tool/Cargo.toml --bin quantum_phase >build-quantum-proof.log 2>&1
status=$?; echo $status >build-quantum-proof.exit; [ "$status" = 0 ] || exit "$status"
python3 check-flag-prefix-zeros.py >flag-prefix-zero.log 2>&1
status=$?; echo $status >flag-prefix-zero.exit; [ "$status" = 0 ] || exit "$status"
python3 run-local-quantum-proofs.py >local-quantum-proofs.log 2>&1
status=$?; echo $status >local-quantum-proofs.exit; echo $status >quantum-proofs.exit; exit "$status"
