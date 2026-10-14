#!/usr/bin/env bash
set -u
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT" || exit 99
name=toffoli-bank-loan-native-20261014
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/toffoli-target
ulimit -v 16777216
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  git status --porcelain
  sha256sum src/point_add/y15_onefold.rs src/point_add/toffoli_bank_loan.rs src/point_add/toffoli_bank_tests.rs src/point_add/toffoli_native_fold.rs
  printf '%s\n' 'command: cargo test --offline --locked --release --bin build_circuit toffoli_bank -- --nocapture --test-threads=1'
  printf '%s\n' 'virtual memory limit KiB:16777216; build threads4; runtime threads1; allnewphasecoefficients covered inroomyfixture'
} > "$name.settings"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit toffoli_bank -- --nocapture --test-threads=1
status=$?
printf '%s\n' "$status" > "$name.exit"
exit "$status"
