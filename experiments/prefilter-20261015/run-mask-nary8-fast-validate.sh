#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-nary8-fast-validate.pid
trap 'echo $? > evidence/mask-nary8-fast-validate.exit' EXIT
free -m > evidence/mask-nary8-fast-validate.resources
gcc -O3 -march=native -fPIC -shared mask_nary8_fast.c -o libmask_nary8_fast.so > evidence/mask-nary8-fast-build.log 2>&1 || exit $?
prlimit --as=2147483648 -- python3 bench-mask-nary8-fast.py > evidence/mask-nary8-fast-runtime.log 2>&1 || exit $?
sha256sum mask_nary8_fast.c libmask_nary8_fast.so bench-mask-nary8-fast.py evidence/mr-mask-tip-v3-nary8.bin evidence/mask-nary8-fast-runtime.json > evidence/mask-nary8-fast-validation.sha256
