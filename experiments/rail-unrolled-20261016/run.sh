#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-unrolled-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/rail-unrolled-20261016/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 16777216
python3 prepare.py > prepare.log 2>&1
/usr/bin/time -v gcc -O3 -march=native -fPIC -shared rail8_unrolled.c -o librail8_unrolled.so > build.log 2>&1
python3 verify.py > verify.log 2>&1
