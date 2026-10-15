#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/back-seam-repair-20261016
echo $$ >phase-proofs.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/seam-phase-repair-20261016/tool/target
python3 prepare-phase-proofs.py >prepare-phase-proofs.log 2>&1
status=$?;echo "$status" >prepare-phase-proofs.exit;[ "$status" = 0 ] || exit "$status"
cargo test --release --offline --manifest-path tool/Cargo.toml --bin phase_primitive -- --test-threads=1 >phase-algebra-tests.log 2>&1
status=$?;echo "$status" >phase-algebra-tests.exit;[ "$status" = 0 ] || exit "$status"
cargo build --release --offline --manifest-path tool/Cargo.toml --bin phase_primitive >build-phase-proofs.log 2>&1
status=$?;echo "$status" >build-phase-proofs.exit;[ "$status" = 0 ] || exit "$status"
for j in 0 1;do
 for mode in old new;do
  "$CARGO_TARGET_DIR/release/phase_primitive" "$mode-component-$j.bin" 0 >"$mode-phase-contract-$j.json" 2>"$mode-phase-contract-$j.log"
  status=$?;echo "$status" >"$mode-phase-contract-$j.exit";[ "$status" = 0 ] || exit "$status"
 done
 "$CARGO_TARGET_DIR/release/phase_primitive" "negative-wrong-clifford-$j.bin" 0 >"negative-phase-contract-$j.json" 2>"negative-phase-contract-$j.log"
 status=$?;echo "$status" >"negative-phase-contract-$j.exit";[ "$status" != 0 ] || exit 1
done
echo 0 >phase-proofs.exit
