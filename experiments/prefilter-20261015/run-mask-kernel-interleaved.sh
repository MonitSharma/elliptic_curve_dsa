#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-kernel-interleaved.pid
trap 'echo $? > evidence/mask-kernel-interleaved.exit' EXIT
free -m > evidence/mask-kernel-interleaved.resources
prlimit --as=2147483648 -- python3 compare-mask-kernels.py > evidence/mask-kernel-interleaved.log 2>&1
