#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-fast-20261015
echo $$ > batch.pid
trap 'rc=$?; echo "$rc" > batch.exit' EXIT
ulimit -v 8388608
uptime
free -g
cat scalar_fixed.c batch_table.c > scalar_batch.c
cc -O3 -march=native -fPIC -shared -Isecp256k1 -Isecp256k1/src scalar_batch.c secp256k1/src/precomputed_ecmult.c secp256k1/src/precomputed_ecmult_gen.c -o libscalar_fast_batch.so > batch-compile.log 2>&1
cc -O3 bench_pairs.c -L. -Wl,-rpath,/home/hclau/ecdsa_research/scalar-fast-20261015 -lscalar_fast_batch -o bench_pairs > batch-bench-compile.log 2>&1
/usr/bin/time -v ./bench_pairs batch-vectors.tsv > batch.out 2> batch-bench.log
sha256sum scalar_batch.c bench_pairs.c libscalar_fast_batch.so batch-vectors.tsv > batch-hashes.sha256
