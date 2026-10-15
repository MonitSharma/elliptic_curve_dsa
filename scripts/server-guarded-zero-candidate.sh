#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/followup-20261015
candidate="$root/b3-guarded-zero"
evidence="$root/guarded-zero-evidence"
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR="$evidence/target"
export RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
cd "$candidate"
git rev-parse HEAD
git status --short
python3 "$root/research-receipt.py" "$candidate" "$evidence/before"
cargo test --release --locked --offline --bin build_circuit guarded_zero -- --nocapture --test-threads=1 > "$evidence/tests.log" 2>&1
# The original benchmark builds, serializes and scores the exact final source.
# Its outcome is retained even on failure; no rerun or packet/nonce selection.
set +e
/usr/bin/time -v bash ./benchmark.sh --note 'Exact conservative guarded-zero CCX removal from public B3; original nonce unchanged; first and only full evaluation of this source' > "$evidence/benchmark.log" 2>&1
rc=$?
set -e
printf '%s\n' "$rc" > "$evidence/benchmark.exit"
python3 "$root/research-receipt.py" "$candidate" "$evidence/terminal" --log "$evidence/benchmark.log" --exit "$evidence/benchmark.exit" --stream "$candidate/ops.bin" --score "$candidate/score.json" --full-benchmark
exit "$rc"
