#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-nary8-validate.pid
trap 'echo $? > evidence/mask-nary8-validate.exit' EXIT
free -m > evidence/mask-nary8-validate.resources
gcc -O3 -march=native -fPIC -shared mask_nary8.c -o libmask_nary8.so > evidence/mask-nary8-build.log 2>&1 || exit $?
while ! test -f evidence/mask-nary8-compile.exit; do sleep 2; done
if test "$(cat evidence/mask-nary8-compile.exit)" != 0; then exit 3; fi
prlimit --as=2147483648 -- python3 bench-mask-nary8.py > evidence/mask-nary8-runtime.log 2>&1 || exit $?
sha256sum mask_nary8.c libmask_nary8.so compile-mask-nary8.py verify-mask-nary8.py bench-mask-nary8.py evidence/mr-mask-tip-v3-nary8.bin evidence/mr-mask-tip-v3-nary8.nodeids-u32le.bin evidence/mr-mask-tip-v3-nary8.termids-u32le.bin evidence/mask-nary8-verification.json evidence/mask-nary8-runtime.json > evidence/mask-nary8-validation.sha256
