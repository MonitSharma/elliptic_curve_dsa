#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/rail-tail64-20261016
trap 'echo $? > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 16777216
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 prepare.py > prepare.log 2>&1
/usr/bin/time -v gcc -O3 -march=native -fPIC -shared rail8_tail64.c -o librail8_tail64.so > build.log 2>&1
/usr/bin/time -v python3 verify.py > verify.log 2>&1
