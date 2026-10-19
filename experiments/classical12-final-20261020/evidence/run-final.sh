#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/classical12-final-20261020
cd "$r"
cleanup() {
 rc=$?
 if [ -f "$r/historical-results.tsv" ] && [ -f "$r/candidate/results.tsv" ] && ! cmp -s "$r/historical-results.tsv" "$r/candidate/results.tsv"; then
  cp "$r/candidate/results.tsv" "$r/observed-results-on-exit.tsv"
  cp "$r/historical-results.tsv" "$r/candidate/results.tsv"
 fi
 printf '%s\n' "$rc" > "$r/final.exit"
}
trap cleanup EXIT
export RESEARCH_SLOTS=3
python3 - <<'PY'
import hashlib
from pathlib import Path
expected={'/home/hclau/ecdsa_research/autonomous-20261019/preflight_v15.py': 'c850285e79899ff098af888d5a6184662f5d68a52558fdc5f514476f4e4c58d2', '/home/hclau/ecdsa_research/autonomous-20261019/resource_registry.py': '7484340a68dfdab93c9d947aece29d43011787b02496575e925a23d76acc0c16'}
for name,h in expected.items():
 with Path(name).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,'Changed immutable resource profile'
PY
python3 ../autonomous-20261019/preflight_v15.py > final-preflight.json
ulimit -v 50331648
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTFLAGS='-C linker=/usr/bin/gcc'
unset RUSTUP_TOOLCHAIN CARGO_TARGET_DIR
python3 finalize.py prepare > prepare.log 2>&1
(
cd "$r/candidate"
git show HEAD:results.tsv > "$r/historical-results.tsv"
for test in frozen_cache_product67 classical_factors_xor classical_xor_control classical_wide; do
 cargo test --release --locked --offline --bin build_circuit "$test" -- --test-threads=1 > "$r/tests-$test.log" 2>&1
done
cargo build --release --locked --offline --bin build_circuit > "$r/build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "$r/generate.log" 2>&1
python3 "$r/finalize.py" native > "$r/native-verification.log" 2>&1
cp ops.bin "$r/native-selected.ops.bin"
python3 "$r/finalize.py" tailcheck > "$r/tailcheck.log" 2>&1
nonce=$(python3 -c "import json;print(json.load(open('$r/SOURCE_FREEZE.json'))['nonce'])")
./benchmark.sh --note "queue-only classical12 exact source optimization; lowest-pass nonce $nonce" > "$r/benchmark.log" 2>&1
python3 "$r/finalize.py" benchmark > "$r/benchmark-verification.log" 2>&1

)
