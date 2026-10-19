#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/scalar-window-20261019
old=/home/hclau/ecdsa_research/scalar-fast-20261015
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/scalar-window-20261019/run.exit' EXIT
python3 ../autonomous-20261019/preflight_v12.py > preflight.json
sha256sum *.py run.sh ../autonomous-20261019/preflight_v12.py > SOURCE.sha256
ulimit -v 33554432
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 prepare.py > prepare.log 2>&1
gcc -O3 -march=native -fPIC -shared -I"$old" -I"$old/secp256k1" -I"$old/secp256k1/src" scalar_extended.c "$old/secp256k1/src/precomputed_ecmult.c" "$old/secp256k1/src/precomputed_ecmult_gen.c" -o libscalar_extended.so > build.log 2>&1
sha256sum scalar_extended.c libscalar_extended.so "$old/VENDOR.txt" "$old/public_comb.h" "$old/secp256k1/src/precomputed_ecmult.c" "$old/secp256k1/src/precomputed_ecmult_gen.c" > BUILD_INPUTS.sha256
for pair in 'frozen 20' 'extended 20' 'extended 22' 'extended 24'; do
 python3 probe.py $pair > "${pair/ /-}.log" 2>&1
done
python3 summarize.py > summary.log 2>&1
