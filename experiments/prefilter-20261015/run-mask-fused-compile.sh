#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-fused-compile.pid
trap 'echo $? > evidence/mask-fused-compile.exit' EXIT
free -m > evidence/mask-fused-compile.resources
prlimit --as=2147483648 -- python3 compile-mask-fused.py > evidence/mask-fused-compile.log 2>&1 || exit $?
prlimit --as=2147483648 -- python3 verify-mask-fused.py > evidence/mask-fused-verification.log 2>&1
