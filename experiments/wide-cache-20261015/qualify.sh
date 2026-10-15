#!/usr/bin/env bash
# Queue mode: this launcher never submits externally.
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
cd "$root"
echo $$ > qualify.pid
trap 'rc=$?; echo "$rc" > "$root/qualify.exit"' EXIT
while test ! -f run.exit || test ! -f replay.exit || test ! -f parent.exit; do sleep 5; done
test "$(cat run.exit)" = 0
test "$(cat replay.exit)" = 0
test "$(cat parent.exit)" = 0
python3 summarize.py evidence > evidence/paired-summary.json
python3 -c 'import json; d=json.load(open("evidence/paired-summary.json")); assert d["passes_failure_gate"]; assert d["mean_T_saving"]>15'
cp evidence/candidate.patch evidence/frozen-candidate.patch
cp evidence/source.sha256 evidence/frozen-source.sha256
cp evidence/stream.sha256 evidence/frozen-stream.sha256
uptime > evidence/screen-preflight.txt
free -g >> evidence/screen-preflight.txt
ulimit -v 50331648
/usr/bin/time -v /home/hclau/ecdsa_research/nonce-screen-20261015/screen/target/release/nonce_screen candidate/ops.bin 1 20000 16 evidence/screen.jsonl > evidence/screen.out 2> evidence/screen.err
python3 finalize.py
cd "$root/candidate"
ln -s ../target target
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR="$root/target"
uptime > "$root/evidence/benchmark-preflight.txt"
free -g >> "$root/evidence/benchmark-preflight.txt"
set +e
/usr/bin/time -v ./benchmark.sh > "$root/evidence/benchmark.log" 2>&1
rc=$?
set -e
echo "$rc" > "$root/evidence/benchmark.exit"
sha256sum ops.bin > "$root/evidence/final-stream.sha256"
test "$rc" = 0
cp score.json "$root/evidence/score.json"
cp results.tsv "$root/evidence/benchmark-results.tsv"
# Benchmark appends historical results; preserve evidence, then restore that protected file.
git restore --source=HEAD -- results.tsv
sha256sum src/bin/eval_circuit.rs src/sim.rs src/circuit.rs src/weierstrass_elliptic_curve.rs benchmark.sh Cargo.toml Cargo.lock rust-toolchain > "$root/evidence/final-protected.sha256"
cmp "$root/evidence/protected.sha256" "$root/evidence/final-protected.sha256"
git diff HEAD > "$root/evidence/final-candidate.patch"
git ls-files --others --exclude-standard src/point_add | while read -r f; do git diff --no-index /dev/null "$f" || test $? = 1; done >> "$root/evidence/final-candidate.patch"
sha256sum src/point_add/*.rs > "$root/evidence/final-source.sha256"
/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census ops.bin wide-cache-final-v1 0 4096 16 "$root/evidence/final-census.jsonl" > "$root/evidence/final-census.log" 2>&1
date -Is > "$root/evidence/qualified-at.txt"
