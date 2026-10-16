#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/payload-model-20261016
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -Is > preflight-source-t0.log
uptime >> preflight-source-t0.log
free -h >> preflight-source-t0.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight-source-t0.log
python3 source-t0-model/parallel-recovered.py /home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv source-t0-population 7 > source-t0-population.log 2>&1
echo "$?" > source-t0-population.exit
