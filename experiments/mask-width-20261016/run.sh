#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/mask-width-20261016
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 16777216
python3 prepare.py
gcc -O3 -shared -fPIC -mavx512f -mavx2 mask_width.c -o libmask_width.so > build.log 2>&1
python3 verify.py > validation.log 2>&1
