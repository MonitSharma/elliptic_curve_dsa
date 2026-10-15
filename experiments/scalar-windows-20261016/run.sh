#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-windows-20261016
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 12582912
python3 prepare.py
old=/home/hclau/ecdsa_research/scalar-fast-20261015
cc -O3 -march=native -fPIC -shared -I"$old/secp256k1" -I"$old/secp256k1/src" scalar_batch.c "$old/secp256k1/src/precomputed_ecmult.c" "$old/secp256k1/src/precomputed_ecmult_gen.c" -o libscalar_windows.so > build.log 2>&1
for window in 18 20 21 22; do python3 verify-window.py "$window" > "window$window.log" 2>&1; done
