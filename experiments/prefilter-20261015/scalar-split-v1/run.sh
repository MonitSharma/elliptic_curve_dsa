#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015/scalar-split-v1
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > resources.log
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> resources.log
printf '%s  %s\n' 3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f ../../scalar-fast-20261015/libscalar_fast_batch.so | sha256sum --check || exit $?
cmp scalar_batch_original.c ../../scalar-fast-20261015/scalar_batch.c || exit $?
cmp public_comb.h ../../scalar-fast-20261015/public_comb.h || exit $?
sha256sum scalar_batch_original.c public_comb.h scalar_split.c scalar_split.h validate-bench.py ../../scalar-fast-20261015/scalar_batch.c ../../scalar-fast-20261015/libscalar_fast_batch.so > before.sha256
git --no-optional-locks -C ../../scalar-fast-20261015/secp256k1 rev-parse HEAD > vendor-head.txt
if test "$(cat vendor-head.txt)" != 1a53f4961f337b4d166c25fce72ef0dc88806618; then exit 3; fi
git --no-optional-locks -C ../../scalar-fast-20261015/secp256k1 diff --exit-code > vendor-diff.log || exit $?
cc -O3 -march=native -fPIC -shared -I../../scalar-fast-20261015 -I../../scalar-fast-20261015/secp256k1 -I../../scalar-fast-20261015/secp256k1/src scalar_split.c ../../scalar-fast-20261015/secp256k1/src/precomputed_ecmult.c ../../scalar-fast-20261015/secp256k1/src/precomputed_ecmult_gen.c -o libscalar_split.so > build.log 2>&1 || exit $?
timeout 600 /usr/bin/time -v prlimit --as=8589934592 -- python3 validate-bench.py > validation-benchmark.log 2> validation-benchmark.err || exit $?
sha256sum scalar_batch_original.c public_comb.h scalar_split.c scalar_split.h validate-bench.py ../../scalar-fast-20261015/scalar_batch.c ../../scalar-fast-20261015/libscalar_fast_batch.so > after.sha256
cmp before.sha256 after.sha256
