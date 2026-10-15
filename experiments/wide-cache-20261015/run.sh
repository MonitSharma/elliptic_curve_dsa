#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
mkdir -p "$root/evidence"
echo $$ > "$root/run.pid"
trap 'rc=$?; echo "$rc" > "$root/run.exit"' EXIT
ulimit -v 50331648
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR="$root/target"
uptime > "$root/evidence/preflight.txt"
free -g >> "$root/evidence/preflight.txt"
ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu | head -18 >> "$root/evidence/preflight.txt" || true
python3 "$root/prepare.py" > "$root/evidence/prepare.log" 2>&1
cd "$root/candidate"
git rev-parse HEAD > "$root/evidence/parent.txt"
sha256sum src/bin/eval_circuit.rs src/sim.rs src/circuit.rs src/weierstrass_elliptic_curve.rs benchmark.sh Cargo.toml Cargo.lock rust-toolchain > "$root/evidence/protected.sha256"
cargo test --release --locked --offline --bin build_circuit wide_cache_ -- --nocapture --test-threads=1 > "$root/evidence/tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$root/evidence/build.log" 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/evidence/generation.log" 2>&1
sha256sum ops.bin > "$root/evidence/stream.sha256"
git diff HEAD > "$root/evidence/candidate.patch"
git ls-files --others --exclude-standard src/point_add | while read -r f; do git diff --no-index /dev/null "$f" || test $? = 1; done >> "$root/evidence/candidate.patch"
sha256sum src/point_add/*.rs > "$root/evidence/source.sha256"
census=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
"$census" ops.bin wide-cache-paired-v1 0 4096 16 "$root/evidence/candidate-census.jsonl" > "$root/evidence/candidate-census.log" 2>&1
date -Is > "$root/evidence/completed.txt"
