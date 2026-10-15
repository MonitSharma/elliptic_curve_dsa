#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-repair-20261015
echo $$ > "$root/choice-tests.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/choice-tests.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/test-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/choice-tests-preflight.json"
python3 "$root/prepare-choice-tests.py" > "$root/choice-tests-prepare.log" 2>&1
cd "$root/choice-tests-b3"
cargo test --release --locked --offline --bin build_circuit widened_choice_signed_and_inverse -- --nocapture --test-threads=1 > "$root/choice-tests.log" 2>&1
grep -q 'WIDENED_CHOICE_PASS' "$root/choice-tests.log"
grep -q '1 passed' "$root/choice-tests.log"
sha256sum src/point_add/rail_kernel.rs src/point_add/leapfrog.rs "$root/choice-tests.log" > "$root/choice-tests-bindings.sha256"
