#!/usr/bin/env bash
set -u
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT" || exit 99
name=toffoli-native-fold-20261014
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 CARGO_BUILD_JOBS=4
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/toffoli-target
. /home/hclau/.cargo/env
ulimit -v 16777216
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  git status --porcelain
  sha256sum src/point_add/y15_onefold.rs src/point_add/toffoli_native_fold.rs
  printf '%s\n' 'command: cargo test --offline --locked --release --bin build_circuit toffoli_native_fold -- --nocapture --test-threads=1'
  printf '%s\n' 'virtual memory limit KiB:16777216; runtime threads:1; build threads:4'
} > "$name.settings"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit toffoli_native_fold -- --nocapture --test-threads=1
status=$?
printf '%s\n' "$status" > "$name.exit"
exit "$status"
