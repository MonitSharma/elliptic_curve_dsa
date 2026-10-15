#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/followup-20261015
candidate="$root/b3-guarded-zero"
evidence="$root/guarded-zero-evidence-v2"
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/guarded-zero-evidence/target"
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
cd "$candidate"
# The unchanged harness invokes ./target/release even when Cargo has an external
# target directory. Expose only this candidate's own already-built cache there.
test ! -e target
ln -s "$CARGO_TARGET_DIR" target
test ! -e ops.bin
sha256sum target/release/build_circuit target/release/eval_circuit > "$evidence/binaries.sha256"
python3 "$root/research-receipt.py" "$candidate" "$evidence/before"
set +e
/usr/bin/time -v bash ./benchmark.sh --note 'Exact conservative guarded-zero CCX removal from public B3; original nonce unchanged; first full evaluation, earlier launcher never executed builder' > "$evidence/benchmark.log" 2>&1
rc=$?
set -e
printf '%s\n' "$rc" > "$evidence/benchmark.exit"
python3 "$root/research-receipt.py" "$candidate" "$evidence/terminal" --log "$evidence/benchmark.log" --exit "$evidence/benchmark.exit" --stream "$candidate/ops.bin" --score "$candidate/score.json" --full-benchmark
exit "$rc"
