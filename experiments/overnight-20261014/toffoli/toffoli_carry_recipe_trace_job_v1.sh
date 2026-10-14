#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-carry-trace-v1
evidence=/home/hclau/ecdsa_research/overnight-20261014/toffoli-carry-trace-v1-evidence
cd "$ROOT"
mkdir -p "$evidence"
printf '%s\n' "$$" > "$evidence/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; exit "$rc"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/toffoli-carry-trace-v1-target
export TOFFOLI_CARRY_TRACE=1 HEO_RESEARCH=1 HEO_PHASE_REPORT=1
ulimit -v 16777216
date -u --iso-8601=seconds
hostname
git rev-parse HEAD
git status --short
{
  printf '%s\n' 'build_threads=4 runtime_threads=1 vmem_kib=16777216 dedicated_target=toffoli-carry-trace-v1-target trace_only=1'
  printf '%s\n' 'cargo test --offline --locked --release --bin build_circuit toffoli_carry_recipe_trace_v1 -- --nocapture --test-threads=1'
  sha256sum src/point_add/y15_onefold.rs src/point_add/toffoli_carry_recipe_trace_v1.rs
} > "$evidence/settings.txt"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit toffoli_carry_recipe_trace_v1 -- --nocapture --test-threads=1
find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -executable -name 'build_circuit-*' -exec sha256sum '{}' + > "$evidence/test-binary.sha256"
date -u --iso-8601=seconds
