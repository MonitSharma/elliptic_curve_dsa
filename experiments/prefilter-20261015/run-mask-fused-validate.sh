#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-fused-validate.pid
trap 'echo $? > evidence/mask-fused-validate.exit' EXIT
free -m > evidence/mask-fused-validate.resources
gcc -O3 -march=native -fPIC -shared mask_fused.c -o libmask_fused.so > evidence/mask-fused-build.log 2>&1 || exit $?
while ! test -f evidence/mask-fused-compile.exit; do sleep 2; done
if test "$(cat evidence/mask-fused-compile.exit)" != 0; then exit 3; fi
prlimit --as=2147483648 -- python3 bench-mask-fused.py > evidence/mask-fused-runtime.log 2>&1 || exit $?
sha256sum mask_fused.c libmask_fused.so compile-mask-fused.py verify-mask-fused.py bench-mask-fused.py evidence/mr-mask-tip-v3-fused.bin evidence/mr-mask-tip-v3-fused.nodeids-u32le.bin evidence/mask-fused-verification.json evidence/mask-fused-runtime.json > evidence/mask-fused-validation.sha256
