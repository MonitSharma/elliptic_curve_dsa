#!/usr/bin/env bash
set -uo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
checkout=$root/product-repair57-components-r1
evidence=$root/product-evidence/repair57-components-r1
trap 'rc=$?; echo "$rc" > "$evidence/run.exit"; python3 "$root/research-receipt.py" "$checkout" "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-repair57-components-r1-target RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$checkout"
date -u
hostname
git rev-parse HEAD
git status --short
sha256sum src/point_add/y15_onefold.rs src/point_add/product_repair57_tests.rs src/point_add/product_repair57_kernel.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit product_repair57_tests --no-run > "$evidence/build.log" 2>&1
rc=$?; echo "$rc" > "$evidence/build.exit"; test "$rc" -eq 0 || exit "$rc"
find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -executable -name 'build_circuit-*' -exec sha256sum '{}' \; > "$evidence/native.sha256"
for name in product_repair57_actual104 product_repair57_body_inverse_probe; do
 /usr/bin/time -v cargo test --offline --locked --release --bin build_circuit "$name" -- --nocapture --test-threads=1 > "$evidence/$name.log" 2>&1
 echo "$?" > "$evidence/$name.exit"
done
date -u
