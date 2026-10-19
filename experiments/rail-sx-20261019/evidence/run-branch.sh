#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/rail-sx-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/rail-sx-20261019/branch.exit' EXIT
python3 ../autonomous-20261019/preflight_v12.py > branch-preflight.json
sha256sum sx_branch.c prepare_branch.py run-branch.sh verify.py probe.c ../autonomous-20261019/preflight_v12.py > BRANCH_SOURCE.sha256
ulimit -v 8388608
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 prepare_branch.py > branch-prepare.log 2>&1
/usr/bin/time -v gcc -O3 -march=native -fPIC -shared branch.c -o libbranch.so > build-branch.log 2>&1
sha256sum libbaseline.so libspecialized.so libbranch.so > BRANCH_LIBRARIES.sha256
python3 verify_branch.py > verify-branch.log 2>&1
