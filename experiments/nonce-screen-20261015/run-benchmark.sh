#!/usr/bin/env bash
# Unchanged official benchmark on the final candidate source (smooth + TAIL_NONCE 375).
set -uo pipefail
root=/home/hclau/ecdsa_research/nonce-screen-20261015
cd "$root/candidate"; echo $$ > ../benchmark.pid
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
git -C "$root/candidate" rev-parse HEAD > ../benchmark-base.txt
git -C "$root/candidate" diff --stat HEAD > ../benchmark-diffstat.txt
git -C "$root/candidate" diff HEAD > ../candidate.patch
git -C "$root/candidate" ls-files --others --exclude-standard | while read -r f; do git -C "$root/candidate" diff --no-index /dev/null "$f"; done >> ../candidate.patch
sha256sum src/bin/eval_circuit.rs src/sim.rs src/circuit.rs src/weierstrass_elliptic_curve.rs benchmark.sh Cargo.toml Cargo.lock rust-toolchain > ../protected.sha256
( ulimit -v 33554432; /usr/bin/time -v ./benchmark.sh ) > ../benchmark.log 2>&1; echo "benchmark_exit=$?" > ../benchmark.status
sha256sum ops.bin score.json >> ../benchmark.status 2>/dev/null
cp score.json ../score.json 2>/dev/null
date -Is > ../benchmark.exit
