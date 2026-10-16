#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/wide15-retained4096-20261016
echo $$ > qualification.pid
trap 's=$?; echo "$s" > qualification.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 41943040
while [ ! -f native-launcher.exit ]; do sleep 20; done
test "$(cat native-launcher.exit)" = 0
python3 qualify.py
