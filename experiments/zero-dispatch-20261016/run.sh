#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/zero-dispatch-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 prepare.py > prepare.log 2>&1
cc -O3 -march=skylake-avx512 -fPIC -shared -I. lazy.c -o liblazy.so > build-lazy.log 2>&1
cc -O3 -march=skylake-avx512 -fPIC -shared -I. threaded.c -o libthreaded.so > build-threaded.log 2>&1
python3 bench.py > bench.log 2>&1
