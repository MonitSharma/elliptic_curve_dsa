#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-masks-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/rail-masks-20261016/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 8388608
python3 prepare.py > prepare.log 2>&1
/usr/bin/time -v gcc -O3 -march=native -fPIC -shared rail8_masks.c -o librail8_masks.so > build.log 2>&1
python3 verify.py > verify.log 2>&1
