#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-windows-20261016
echo $$ > retry.pid
trap 'echo $? > retry.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > retry-preflight.json
ulimit -v 12582912
old=/home/hclau/ecdsa_research/scalar-fast-20261015
cc -O3 -march=native -fPIC -shared -I"$old" -I"$old/secp256k1" -I"$old/secp256k1/src" scalar_batch.c "$old/secp256k1/src/precomputed_ecmult.c" "$old/secp256k1/src/precomputed_ecmult_gen.c" -o libscalar_windows.so > retry-build.log 2>&1
while [ ! -f /home/hclau/ecdsa_research/product-filter-cost-20261016/run.exit ]; do sleep 2; done
python3 /home/hclau/ecdsa_research/server-preflight.py > timing-preflight.json
for window in 18 20 21 22; do python3 verify-window.py "$window" > "window$window.log" 2>&1; done
