#!/usr/bin/env bash
set -uo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
checkout=$root/product-repair57-production-sixteen-r1
evidence=$root/product-evidence/repair57-production-sixteen-r1
trap 'rc=$?; echo "$rc" > "$evidence/run.exit"; python3 "$root/research-receipt.py" "$checkout" "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-repair57-production-sixteen-r1-target RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$checkout"
sha256sum "$root/product-evidence/repair57-production-pool/before.json" "$root/product-evidence/repair57-production-pool/after.json" "$root/product-evidence/c5-fold75/pre-y33.bin" > "$evidence/input.sha256"; date -u
hostname
git rev-parse HEAD
git status --short
sha256sum src/point_add/y15_onefold.rs src/point_add/product_repair57_tests.rs src/point_add/product_repair57_kernel.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit product_repair57_tests --no-run > "$evidence/build.log" 2>&1
rc=$?; echo "$rc" > "$evidence/build.exit"; test "$rc" -eq 0 || exit "$rc"
find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -executable -name 'build_circuit-*' -exec sha256sum '{}' \; > "$evidence/native.sha256"
for name in product_repair57_body_inverse_probe; do
 /usr/bin/time -v cargo test --offline --locked --release --bin build_circuit "$name" -- --nocapture --test-threads=1 > "$evidence/$name.log" 2>&1
 rc=$?; echo "$rc" > "$evidence/$name.exit"; test "$rc" -eq 0 || exit "$rc"; grep -q "running 1 test" "$evidence/$name.log" || exit 97; grep -q "1 passed; 0 failed" "$evidence/$name.log" || exit 98; grep -q "REPAIR57_SIXTEEN_BDD_PROVED" "$evidence/$name.log" || exit 99
done
sha256sum "$root/product-evidence/repair57-production-pool/before.json" "$root/product-evidence/repair57-production-pool/after.json" "$root/product-evidence/c5-fold75/pre-y33.bin" > "$evidence/input.sha256"; date -u
