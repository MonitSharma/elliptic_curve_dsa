#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/mask-evaluator-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/mask-evaluator-20261016/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 8388608
gcc -O3 -march=native -fPIC -shared mask8.c -o libmask8.so > build.log 2>&1
python3 verify.py > verify.log 2>&1
