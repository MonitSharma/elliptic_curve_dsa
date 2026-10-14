#!/usr/bin/env bash
set -u
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT" || exit 99
name=toffoli-bank-receipts-v4-20261014
printf '%s\n' "$$" > "$name.pid"
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/toffoli-target
export HEO_PHASE_REPORT=1
export HEO_RESEARCH=1
export TOFFOLI_STREAM_DIR="$ROOT/$name-streams"
mkdir -p "$TOFFOLI_STREAM_DIR"
ulimit -v 16777216
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  git status --porcelain
  sha256sum src/point_add/y15_onefold.rs src/point_add/toffoli_bank_loan.rs src/point_add/toffoli_bank_receipts.rs
  printf '%s\n' 'command: cargo test --offline --locked --release --bin build_circuit toffoli_bank_receipts -- --nocapture --test-threads=1'
  printf '%s\n' '16GiB virtual memory; 4 build threads; 1 runtime; HEO_PHASE_REPORT=1 HEO_RESEARCH=1; builder diagnostic only; require v2 stream hashes equal'
} > "$name.settings"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit toffoli_bank_receipts -- --nocapture --test-threads=1
status=$?
find "$TOFFOLI_STREAM_DIR" -type f -name '*.bin' -exec sha256sum '{}' + > "$name-stream-hashes.txt"
printf '%s\n' "$status" > "$name.exit"
exit "$status"
