#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-nary8-compile.pid
trap 'echo $? > evidence/mask-nary8-compile.exit' EXIT
free -m > evidence/mask-nary8-compile.resources
prlimit --as=3221225472 -- python3 compile-mask-nary8.py > evidence/mask-nary8-compile.log 2>&1 || exit $?
prlimit --as=2147483648 -- python3 verify-mask-nary8.py > evidence/mask-nary8-verification.log 2>&1
