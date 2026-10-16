#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/payload-model-20261016
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -Is > preflight-population.log
uptime >> preflight-population.log
free -h >> preflight-population.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight-population.log
python3 parallel-recovered.py /home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv corrected-population 8 > population.log 2>&1
echo "$?" > population.exit
