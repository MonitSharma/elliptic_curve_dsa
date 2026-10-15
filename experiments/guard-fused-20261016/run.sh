#!/bin/bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/guard-fused-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'echo $? > "$ROOT/run.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
hostname > resources
free -m >> resources
ps -eo pid,pcpu,rss,nlwp,args --sort=-pcpu | head -25 >> resources
sha256sum ../prefilter-20261015/a29-conditional-prefix-v1/public-discrepancy-guard.bin ../prefilter-20261015/libmask_fused.so ../mask-evaluator-20261016/libmask8.so compile-mask-fused.py verify-mask-fused.py make-wrapper.py bench.py > before.sha256
python3 make-wrapper.py > wrapper.log 2>&1
python3 compile-mask-fused.py guard512.bin guard-fused > compile.log 2>&1
python3 verify-mask-fused.py > verify.log 2>&1
python3 bench.py > bench.log 2>&1
sha256sum ../prefilter-20261015/a29-conditional-prefix-v1/public-discrepancy-guard.bin ../prefilter-20261015/libmask_fused.so ../mask-evaluator-20261016/libmask8.so compile-mask-fused.py verify-mask-fused.py make-wrapper.py bench.py > after.sha256
cmp before.sha256 after.sha256
