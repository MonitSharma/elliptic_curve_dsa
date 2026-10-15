#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/recovered-population.exit' EXIT
echo $$ > evidence/recovered-population.pid
ulimit -v 62914560
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
uptime > evidence/recovered-population.resources
free -g >> evidence/recovered-population.resources
ps -eo pid,comm,pcpu,pmem,args --sort=-pcpu | head -20 >> evidence/recovered-population.resources
python3 parallel-recovered.py evidence/census-coordinates4096.tsv evidence/recovered-population 14 > evidence/recovered-population.log 2>&1
