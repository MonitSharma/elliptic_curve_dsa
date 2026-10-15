#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-fast-20261015
echo $$ > build.pid
trap 'rc=$?; echo "$rc" > build.exit' EXIT
ulimit -v 8388608
uptime
free -g
git -C secp256k1 rev-parse HEAD > VENDOR.txt
cp secp256k1/COPYING COPYING.secp256k1
cc -O3 -march=native -fPIC -shared -Isecp256k1 -Isecp256k1/src scalar_fast.c secp256k1/src/precomputed_ecmult.c secp256k1/src/precomputed_ecmult_gen.c -o libscalar_fast.so > compile.log 2>&1
cc -O3 bench.c -L. -Wl,-rpath,/home/hclau/ecdsa_research/scalar-fast-20261015 -lscalar_fast -o bench > bench-compile.log 2>&1
./bench export > vectors.tsv 2> bench.log
sha256sum scalar_fast.c bench.c libscalar_fast.so bench vectors.tsv VENDOR.txt > hashes.sha256
