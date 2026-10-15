#!/usr/bin/env bash
# Build the public product record (4b2ec52f) stream, census it on fresh inputs and time the nonce screener.
set -uo pipefail
root=/home/hclau/ecdsa_research/product-tip-20261015
cd "$root"; echo $$ > tip.pid
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json 2>&1 || true
cd tip
( ulimit -v 33554432; cargo build --release --locked --offline --bin build_circuit --bin eval_circuit ) > ../tip-build.log 2>&1; echo "build_exit=$?" > ../tip.status
( ulimit -v 33554432; /usr/bin/time -v ./target/release/build_circuit ) > ../tip-gen.log 2>&1; echo "gen_exit=$?" >> ../tip.status
sha256sum ops.bin >> ../tip.status
cd "$root"
N=/home/hclau/ecdsa_research/nonce-screen-20261015/screen/target/release/nonce_screen
C=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
/usr/bin/time -f "wall=%e exit=%x" "$N" tip/ops.bin @official > tip-official.txt 2>&1
/usr/bin/time -f "wall=%e exit=%x" "$C" tip/ops.bin tip-4b2ec52f 0 4096 32 tip-census.jsonl 2> tip-census.err
/usr/bin/time -f "wall=%e exit=%x" "$N" tip/ops.bin 1 256 32 tip-screen-1-256.jsonl > tip-screen.out 2> tip-screen.err
date -Is > tip.exit
