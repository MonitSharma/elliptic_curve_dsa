#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/rail-sx-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/rail-sx-20261019/run.exit' EXIT
python3 ../autonomous-20261019/preflight_v12.py > preflight.json
sha256sum *.py *.c run.sh ../autonomous-20261019/preflight_v12.py > SOURCE.sha256
ulimit -v 8388608
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 prepare.py > prepare.log 2>&1
/usr/bin/time -v gcc -O3 -march=native -fPIC -shared baseline.c -o libbaseline.so > build-baseline.log 2>&1
/usr/bin/time -v gcc -O3 -march=native -fPIC -shared specialized.c -o libspecialized.so > build-specialized.log 2>&1
sha256sum libbaseline.so libspecialized.so > LIBRARIES.sha256
python3 verify.py > verify.log 2>&1
