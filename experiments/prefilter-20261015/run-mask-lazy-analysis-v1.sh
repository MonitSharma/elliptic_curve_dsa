#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-lazy-analysis-v1.pid
trap 'echo $? > evidence/mask-lazy-analysis-v1.exit' EXIT
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
free -m > evidence/mask-lazy-analysis-v1.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 >> evidence/mask-lazy-analysis-v1.resources
sha256sum evidence/mr-mask-tip-v3.bin ../mask-evaluator-20261016/libmask8.so mask-lazy-analysis-v1.py > evidence/mask-lazy-analysis-v1-before.sha256
timeout 600 /usr/bin/time -v prlimit --as=8589934592 -- python3 mask-lazy-analysis-v1.py > evidence/mask-lazy-analysis-v1.log 2> evidence/mask-lazy-analysis-v1.err || exit $?
sha256sum evidence/mr-mask-tip-v3.bin ../mask-evaluator-20261016/libmask8.so mask-lazy-analysis-v1.py > evidence/mask-lazy-analysis-v1-after.sha256
cmp evidence/mask-lazy-analysis-v1-before.sha256 evidence/mask-lazy-analysis-v1-after.sha256
