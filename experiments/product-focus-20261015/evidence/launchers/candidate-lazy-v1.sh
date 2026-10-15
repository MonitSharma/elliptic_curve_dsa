#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-focus-20261015
evidence="$root/candidate-lazy-v1-evidence"
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/candidate-lazy-v1-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
python3 "$root/prepare-candidate.py" > "$evidence/prepare.log" 2>&1
cd "$root/candidate-lazy-v1"
ln -s "$CARGO_TARGET_DIR" target
python3 /home/hclau/ecdsa_research/followup-20261015/research-receipt.py "$PWD" "$evidence/before"
cargo test --release --locked --offline --bin build_circuit lazy_cache_ -- --nocapture --test-threads=1 > "$evidence/native.log" 2>&1
grep -q '2 passed; 0 failed' "$evidence/native.log"
set +e
/usr/bin/time -v bash ./benchmark.sh --note 'Exact lazy AND caching in proven idle qubits; frozen inherited tail; first final benchmark of this candidate' > "$evidence/benchmark.log" 2>&1
rc=$?
set -e
printf '%s\n' "$rc" > "$evidence/benchmark.exit"
sha256sum target/release/build_circuit target/release/eval_circuit > "$evidence/binaries.sha256"
python3 /home/hclau/ecdsa_research/followup-20261015/research-receipt.py "$PWD" "$evidence/terminal" --log "$evidence/benchmark.log" --exit "$evidence/benchmark.exit" --stream "$PWD/ops.bin" --score "$PWD/score.json" --full-benchmark
exit "$rc"
