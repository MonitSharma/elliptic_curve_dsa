#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence=$root/product-evidence/repair57-production-bdd
trap 'rc=$?; echo "$rc" > "$evidence/fault.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-repair57-production-bdd-target RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
while ! test -f "$evidence/build.exit"; do sleep 5; done
test "$(cat "$evidence/build.exit")" = 0
cd "$root/product-repair57-production-bdd"
echo '72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622  src/point_add/product_repair57_kernel.rs' | sha256sum -c -
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit product_repair57_tests::kernel::tests -- --nocapture --test-threads=1 > "$evidence/fault-tests.log" 2>&1
grep -q 'running 4 tests' "$evidence/fault-tests.log"
grep -q '4 passed; 0 failed' "$evidence/fault-tests.log"
grep -q 'snapshot_mutation_nested_push_and_phase_fault ... ok' "$evidence/fault-tests.log"
echo REPAIR57_BDD_FAULT_NATIVE_TESTS_VERIFIED
