#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wider-cap-20261016
cd "$root"
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > "$root/run.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR="$root/target"
ulimit -v 33554432
python3 prepare.py > prepare.log 2>&1
for cap in 1792 2048; do
 cd "$root/cap$cap"
 cargo test --release --locked --offline --bin build_circuit -- --test-threads=1 > "$root/cap$cap-tests.log" 2>&1
 cargo build --release --locked --offline --bin build_circuit > "$root/cap$cap-build.log" 2>&1
 /usr/bin/time -v "$root/target/release/build_circuit" > "$root/cap$cap-generate.log" 2>&1
 sha256sum ops.bin > "$root/cap$cap-stream.sha256"
done
cd "$root"
python3 summarize-build.py > build-summary.json
# All streams and labels are fixed before any failure results are inspected.
if python3 -c 'import json;d=json.load(open("build-summary.json"));assert any(x["changed"] for x in d["candidates"])'; then
 C=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
 python3 /home/hclau/ecdsa_research/server-preflight.py > census-preflight.json
 "$C" /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin wider-cap-fixed-20261016 0 4096 4 parent-census.jsonl > parent-census.log 2>&1 &
 p1=$!; echo "$p1" > parent-census.pid
 "$C" cap1792/ops.bin wider-cap-fixed-20261016 0 4096 4 cap1792-census.jsonl > cap1792-census.log 2>&1 &
 p2=$!; echo "$p2" > cap1792-census.pid
 "$C" cap2048/ops.bin wider-cap-fixed-20261016 0 4096 4 cap2048-census.jsonl > cap2048-census.log 2>&1 &
 p3=$!; echo "$p3" > cap2048-census.pid
 wait "$p1"; wait "$p2"; wait "$p3"
fi
