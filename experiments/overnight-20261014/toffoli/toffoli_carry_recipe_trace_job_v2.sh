#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-carry-trace-v2
evidence=/home/hclau/ecdsa_research/overnight-20261014/toffoli-carry-trace-v2-evidence
cd "$ROOT"
mkdir -p "$evidence"
printf '%s\n' "$$" > "$evidence/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; exit "$rc"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/toffoli-carry-trace-v2-target
export TOFFOLI_CARRY_TRACE=1 HEO_RESEARCH=1 HEO_PHASE_REPORT=1
ulimit -v 16777216
date -u --iso-8601=seconds
hostname
git rev-parse HEAD
git status --short
{
  printf '%s\n' 'build_threads=4 runtime_threads=1 vmem_kib=16777216 dedicated_target=toffoli-carry-trace-v2-target trace_only=1 cap1234 per-context-process=1'
  printf '%s\n' 'cargo test --offline --locked --release --bin build_circuit --no-run; then126 independent test-binary processes toffoli_carry_recipe_trace_v2'
  sha256sum src/point_add/y15_onefold.rs src/point_add/toffoli_carry_recipe_trace_v2.rs
} > "$evidence/settings.txt"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit --no-run
mapfile -t binaries < <(find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -executable -name 'build_circuit-*')
test "${#binaries[@]}" -eq 1
binary="${binaries[0]}"
sha256sum "$binary" > "$evidence/test-binary.sha256"
printf 'room\ttick\texit\n' > "$evidence/context-exits.tsv"
for room in 70 60 54 50 46 44 42 41 40 39 38 37 36 35; do
  for tick in 128 129 130 131 132 133 134 135 136; do
    printf 'TOFFOLI_CARRY_CONTEXT_START cap=1234 room=%s tick=%s\n' "$room" "$tick"
    if TOFFOLI_TRACE_ROOM="$room" TOFFOLI_TRACE_TICK="$tick" "$binary" toffoli_carry_recipe_trace_v2 --nocapture --test-threads=1; then rc=0; else rc=$?; fi
    printf '%s\t%s\t%s\n' "$room" "$tick" "$rc" >> "$evidence/context-exits.tsv"
  done
done
date -u --iso-8601=seconds
