#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-fast-20261015
echo $$ > comb.pid
trap 'rc=$?; echo "$rc" > comb.exit' EXIT
ulimit -v 8388608
uptime
free -g
python3 prepare-comb.py
cc -O3 -march=native -fPIC -shared -Isecp256k1 -Isecp256k1/src scalar_fast.c secp256k1/src/precomputed_ecmult.c secp256k1/src/precomputed_ecmult_gen.c -o libscalar_fast_comb.so > comb-compile.log 2>&1
cc -O3 bench_comb.c -L. -Wl,-rpath,/home/hclau/ecdsa_research/scalar-fast-20261015 -lscalar_fast_comb -o bench_comb > comb-bench-compile.log 2>&1
./bench_comb export > comb-vectors.tsv 2> comb-bench.log
sha256sum scalar_fast.c public_comb.h bench_comb.c libscalar_fast_comb.so comb-vectors.tsv > comb-hashes.sha256
