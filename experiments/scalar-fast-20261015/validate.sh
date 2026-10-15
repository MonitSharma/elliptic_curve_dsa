#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-fast-20261015
echo $$ > validate.pid
trap 'rc=$?; echo "$rc" > validate.exit' EXIT
ulimit -v 8388608
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
uptime
free -g
python3 export-validation.py
cd verify-reference
cargo build --release --locked --offline > ../reference-build.log 2>&1
cd ..
./verify-reference/target/release/product_paired_diagnostic validation-vectors.tsv > reference-validation.log 2>&1
sha256sum validation-vectors.tsv verify-reference/src/main.rs /home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline/src/weierstrass_elliptic_curve.rs libscalar_fast_batch.so > reference-hashes.sha256
cc -O3 bench_pairs.c -L. -Wl,-rpath,/home/hclau/ecdsa_research/scalar-fast-20261015 -lscalar_fast_batch -o bench_pairs
for window in 18 20; do
 /usr/bin/time -v ./bench_pairs "batch-$window-vectors.tsv" "$window" > "batch-$window.out" 2> "batch-$window-bench.log"
done
