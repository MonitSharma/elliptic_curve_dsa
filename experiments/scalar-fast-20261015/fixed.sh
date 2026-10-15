#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-fast-20261015
echo $$ > fixed.pid
trap 'rc=$?; echo "$rc" > fixed.exit' EXIT
ulimit -v 8388608
uptime
free -g
python3 prepare-fixed.py
cc -O3 -march=native -fPIC -shared -Isecp256k1 -Isecp256k1/src scalar_fixed.c secp256k1/src/precomputed_ecmult.c secp256k1/src/precomputed_ecmult_gen.c -o libscalar_fast_fixed.so > fixed-compile.log 2>&1
cc -O3 bench_fixed.c -L. -Wl,-rpath,/home/hclau/ecdsa_research/scalar-fast-20261015 -lscalar_fast_fixed -o bench_fixed > fixed-bench-compile.log 2>&1
for window in 16 20; do
 /usr/bin/time -v ./bench_fixed export "$window" > "fixed-$window-vectors.tsv" 2> "fixed-$window-bench.log"
done
sha256sum scalar_fixed.c bench_fixed.c libscalar_fast_fixed.so fixed-*-vectors.tsv > fixed-hashes.sha256
